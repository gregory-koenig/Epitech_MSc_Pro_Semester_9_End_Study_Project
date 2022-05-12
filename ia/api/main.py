# from models.naive_bayes import train, predict
import logging
import json
import pandas
import uvicorn
from models.naive_bayes import NaiveBayesModel

from fastapi import FastAPI
from random import randint
from random import choice

description = """
Machine Learning Compiler API 🧠🌐

## Data
Retrieving data from our Naive Bayes model to use for visualization

## Train
Training machine learning model receiving a JSON message containing a pandas DataFrame with the following format
```
{
    "ast_vec": *ast*,
    "algo_vec": *algorithm*
}
```

## Predict *(to be implemented)*
Send unlabelled message containing AST to the model and retrieve the best way to compile that algorithm with that AST

"""

logger = logging.getLogger()
app = FastAPI(
    title="ML Compiler API",
    description=description,
    version="0.0.1",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
model = NaiveBayesModel()


@app.get("/data")
def data():
    """
    Retrieving data from our model to understand how it works and creating visualizing that data \n
    :return: model inner workings data
    """
    message = {
        "theta": model.model.theta_.tolist(),
        "epsilon": model.model.epsilon_,
        "sigma": model.model.sigma_.tolist(),
        "var": model.model.var_.tolist(),
        "n_features": model.model.n_features_in_,
        "classes": model.model.classes_.tolist(),
        "classes_prior": model.model.class_prior_.tolist(),
    }
    return message


@app.get("/")
def connected():
    return {
        "connected": True
    }


@app.get("/train")
def train():
    """
    Route used to train machine learning model receiving a dataframe as JSON as an input \n
    :param msg: JSON dictionary containing AST data to convert into a dataframe {"ast_vec": *ast*, "algo_vec": *algorithm*} \n
    :return: status about training (success, error, other...)
    """
    success = False
    message = {}
    df = generate_ast()
    #df = check_json_to_dataframe(msg)
    try:
        model.train(df)
        success = True
    except Exception as e:
        logger.error(f"Encountered error at model training: {e}")
    message.update({"training": success})
    message.update(data())
    logger.info(f"Sending out message with success : {message['training']}")
    return message


def check_json_to_dataframe(msg):
    """

    :param msg:
    :return:
    """
    try:
        dic = json.loads(msg)
        df = pandas.DataFrame.from_dict(dic)    # constitue une dataframe avec les données du message
        return df
    except json.decoder.JSONDecodeError as jsn_e:
        logger.error(f"Couldn't load JSON properly, skipping message. {jsn_e}")
    except TypeError as te:
        logger.error(f"Couldn't build dataframe from json : {te}")


def generate_ast():
    dic = {
        "ast_vec": [
            f"\"LITERAL,{randint(0, 9)}\", \"OPERATOR,{choice(['-', '+', '*', '/', '%'])}\", \"LITERAL {randint(0, 10)}\""
            for _ in range(500)],
        "algo_vec": [
            f"{randint(0, 3)}, {randint(0, 3)}, {randint(0, 3)}, {randint(0, 3)}, {randint(0, 3)}, {randint(0, 3)}" for
            _ in range(500)]
    }
    df = pandas.DataFrame.from_dict(dic)
    return df


@app.get("/predict")
def predict():
    msg = {"ast_vec": ['"LITERAL,5", "OPERATOR,+", "LITERAL,5"']}
    df = pandas.DataFrame.from_dict(msg)        # a enlever mais on vérifie manuellement que ça marche
    # df = check_json_to_dataframe(msg)
    logger.info(df)
    print(df)
    prediction = model.predict(df)
    print(prediction)
    logger.info(type(prediction))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    uvicorn.run("main:app", reload=True, host='0.0.0.0', port=8008)
