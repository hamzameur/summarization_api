# Summarization API
This API allows user to store a text and request a summary of it.

Typical workflow:

1. send a `POST` request to store text in a database and get a text id
2. send a `GET` request to retrieve the text corresponding to a text id
3. send a `GET` request to get a summary of the text corresponding to a text id

For the summarization service the API uses the gensim implemetation of TextRank algorithm (extractive summarization). See documentation here : https://radimrehurek.com/gensim_3.8.3/auto_examples/tutorials/run_summarization.html

## 1. Start the API

First you need to clone this project :

```
$ git clone https://github.com/hamzameur/summarization_api.git
```
Then you need to check out the  `summarization_api` directory :

```
$ cd summarization_api
```

### Docker (recommended)

If you got Docker installed then you simply need to run the following commands:

```
$ sudo docker build . -t summarization_api
```
Once you make sure the image has been successfuly built, run the following command :
```
$ sudo docker run -p 5000:5000 -d summarization_api
```

### Poetry

If you use poetry then you can run the following command in the `summarization_api` directory to install the virtual environment (python version 3.8.11):
```
$ poetry install
```
Once the environment is installed, you can run the following commands to run the api (feel free to change the port):
```
$ export FLASK_APP=summarization_api/views.py
$ poetry run python -m flask run --host=0.0.0.0 --port=5000
```
You will see the following output :
```
* Serving Flask app 'summarization_api/views.py'
* Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://192.168.1.83:5000
Press CTRL+C to quit
```

### virtualenv

If you use virtualenv you can run the following commands in the `summarization_api` directory (python version 3.8.11:
```
$ export FLASK_APP=summarization_api/views.py
$ python3 -m venv env
$ source env/bin/activate
$ python -m pip install -r requirements.txt
$ python -m flask run --host=0.0.0.0 --port=5000
```
You will see the following output :
```
* Serving Flask app 'summarization_api/views.py'
* Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://192.168.1.83:5000
Press CTRL+C to quit
```
## 2. Use the API

The API implements the following 3 features : 

1. store text in a database and get a text id via a `POST` call to the `/store-text-and-get-id` service. You should provide the text in the `text` parameter in the form.
2. retrieve the text corresponding to a text id via a `GET` call to the `/texts/{textId}` service
3. get a summary of the text corresponding to a text id via a `GET` call to the `/texts/{textId}/summarize` service


### sample requests : 1- store and retrieve text

Once you run the API using instructions from section 1. you can try out the following requests :
```
$ curl -d "text=Hello, world !" -X POST http://localhost:5000/store-text-and-get-id
```
Output:
```
{"textId":"da1180d4c2cec7514b8f9707719e6fce5d872e393860b54a848b4060a8463a7c"}
```
You can retrieve the text you just saved using the following `GET` call:
```
$ curl http://localhost:5000/texts/da1180d4c2cec7514b8f9707719e6fce5d872e393860b54a848b4060a8463a7c
```
Output:
```
{"text":"Hello, world !","textId":"da1180d4c2cec7514b8f9707719e6fce5d872e393860b54a848b4060a8463a7c"}
```

###  sample requests : 2- store text stored in a `.txt` file and retrieve summary

We have provided an example of a larger text in the `sample_text.txt` file for demo purposes :

```
$ curl -d "@sample_text.txt" -X POST http://localhost:5000/store-text-and-get-id
```
Output:
```
{"textId":"7f52f7e7c217848eaa291544784fc44735ac0cd14988cb4f432fad4754d2c49d"}
```
#### request a summary using default summarization parameter
you can just run the following command:
```
$ curl http://localhost:5000/texts/7f52f7e7c217848eaa291544784fc44735ac0cd14988cb4f432fad4754d2c49d/summarize
```
Output :
```
{
  "summary":"Morpheus awakens Neo to the real world, a ravaged wasteland where most of humanity have been captured by a race of machines that live off of the humans' body heat and electrochemical energy and who imprison their minds within an artificial reality known as the Matrix.",
  "summaryParameters":{"ratio":0.2},
  "textId":"7f52f7e7c217848eaa291544784fc44735ac0cd14988cb4f432fad4754d2c49d"
}
```
#### request a summary using custom ratio
you can just run the following command for a ratio of 0.19:
```
$ curl http://localhost:5000/texts/7f52f7e7c217848eaa291544784fc44735ac0cd14988cb4f432fad4754d2c49d/summarize?ratio=0.19
```
Output :
```
{
  "summary":"Morpheus awakens Neo to the real world, a ravaged wasteland where most of humanity have been captured by a race of machines that live off of the humans' body heat and electrochemical energy and who imprison their minds within an artificial reality known as the Matrix.",
  "summaryParameters":{"ratio":0.19},
  "textId":"7f52f7e7c217848eaa291544784fc44735ac0cd14988cb4f432fad4754d2c49d"
}
```

#### request a summary using custom word count
you can just run the following command for a word count of 100:
```
$ curl http://localhost:5000/texts/7f52f7e7c217848eaa291544784fc44735ac0cd14988cb4f432fad4754d2c49d/summarize?wordCount=100
```
Output :
```
{
  "summary":"By day he is an average computer programmer and by night a hacker known as Neo. Neo has always questioned his reality, but the truth is far beyond his imagination.\nMorpheus awakens Neo to the real world, a ravaged wasteland where most of humanity have been captured by a race of machines that live off of the humans' body heat and electrochemical energy and who imprison their minds within an artificial reality known as the Matrix.\nAs a rebel against the machines, Neo must return to the Matrix and confront the agents: super-powerful computer programs devoted to snuffing out Neo and the entire human rebellion.",
  "summaryParameters":{"wordCount":100},
  "textId":"7f52f7e7c217848eaa291544784fc44735ac0cd14988cb4f432fad4754d2c49d"
 }
```
### Small notes
1. if you provide both `ratio` and `wordCount` parameters, the `ratio` will be used and `wordCount` will be ignored
2. if you provide a ratio equal to zero or a non-float ratio, then  the default value of 0.2 will be used
3. if you provide a word count equal to zero or a non-int word count, then  the default value of 10 will be used
## 3. Test the code
Run the following command :
```
$ poetry run pytest
```
or if you would like to see the coverage for each module : 
```
$ poetry run pytest --cov=summarization_api
```


