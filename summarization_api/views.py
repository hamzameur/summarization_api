from flask import Flask, request, jsonify

from gensim.summarization import summarize

from summarization_api.model import (
    SummarizationApiException,
    ApiExceptionName,
    TextIdNotFoundError,
)
from summarization_api.storage_utils import SqlTextHandler

app = Flask(__name__)

DEFAULT_RATIO: float = 0.2
DEFAULT_WORD_COUNT: int = 10


KEY_WORD_COUNT: str = "wordCount"
KEY_RATIO: str = "ratio"
KEY_SUMMARY: str = "summary"
KEY_SUMMARY_PARAMETERS: str = "summaryParameters"
KEY_TEXT: str = "text"
KEY_TEXT_ID: str = "textId"
KEY_WARNING: str = "warning"

REQUEST_PARAM_WORD_COUNT: str = KEY_WORD_COUNT
REQUEST_PARAM_RATIO: str = KEY_RATIO


TEXT_HANDLER: SqlTextHandler = SqlTextHandler("texts.db")


@app.errorhandler(SummarizationApiException)
def handle_api_error(e: SummarizationApiException):
    return jsonify(e.build_message()), e.code


@app.route("/texts", methods=["POST"])
def store_text_and_get_id():
    if KEY_TEXT not in request.form:
        raise SummarizationApiException(
            code=400,
            name=ApiExceptionName.MISSING_REQUIRED_PARAMETER,
            description="text to store is missing",
        )
    text = request.form[KEY_TEXT]
    text_id: str = TEXT_HANDLER.store_text_and_get_id(text=text)
    return jsonify({KEY_TEXT_ID: text_id})


@app.route("/texts/<text_id>", methods=["GET"])
def get_text_from_id(text_id: str):
    try:
        text: str = TEXT_HANDLER.get_text_from_id(text_id=text_id)
        return jsonify({KEY_TEXT_ID: text_id, KEY_TEXT: text})

    except TextIdNotFoundError as e:
        raise SummarizationApiException(
            code=404,
            name=ApiExceptionName.ID_NOT_FOUND,
            description=str(e),
        )


@app.route("/texts/<text_id>/summarize", methods=["GET"])
def summarize_text(text_id: str):
    try:
        text: str = TEXT_HANDLER.get_text_from_id(text_id=text_id)

    except TextIdNotFoundError as e:
        raise SummarizationApiException(
            code=404,
            name=ApiExceptionName.ID_NOT_FOUND,
            description=str(e),
        )
    else:

        response_dict: dict = {KEY_TEXT_ID: text_id}

        if REQUEST_PARAM_RATIO in request.args:
            try:
                ratio = float(request.args[REQUEST_PARAM_RATIO])
                if ratio == 0:
                    ratio = DEFAULT_RATIO
            except ValueError:
                ratio = DEFAULT_RATIO
            summarization_params = {"ratio": ratio}
            response_dict[KEY_SUMMARY_PARAMETERS] = {KEY_RATIO: ratio}

        elif REQUEST_PARAM_WORD_COUNT in request.args:
            try:
                word_count = int(request.args[REQUEST_PARAM_WORD_COUNT])
                if word_count == 0:
                    word_count = DEFAULT_WORD_COUNT

            except ValueError:
                word_count = DEFAULT_WORD_COUNT
            summarization_params = {"word_count": word_count}
            response_dict[KEY_SUMMARY_PARAMETERS] = {KEY_WORD_COUNT: word_count}
        else:
            summarization_params = {"ratio": DEFAULT_RATIO}
            response_dict[KEY_SUMMARY_PARAMETERS] = {KEY_RATIO: DEFAULT_RATIO}
        try:
            summary = summarize(text=text, **summarization_params)
            response_dict[KEY_SUMMARY] = summary
            return jsonify(response_dict)
        except ValueError as e:
            if str(e) == "input must have more than one sentence":
                raise SummarizationApiException(
                    code=501,
                    name=ApiExceptionName.TEXT_TOO_SHORT,
                    description="the current summarizer does not support text with"
                    " less than two sentences",
                )
            else:
                raise e
