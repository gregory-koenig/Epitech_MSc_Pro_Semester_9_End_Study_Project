import logging

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score

logger = logging.getLogger()


class NaiveBayesModel:
    # TODO Trouver un moyen d'expliciter les données du modèle et montrer comment il fonctionne et
    #  comment il sort ce qu'on a
    def __init__(self):
        self.label_features = []
        self.ast_features = []
        self.model = GaussianNB()

    def train(self, dataframe):
        for i in range(len(dataframe)):
            self.label_features.append(dataframe['algo_vec'][i])
            self.ast_features.append(dataframe['ast_vec'][i])

        le = LabelEncoder()
        # encodedLabels = le.fit_transform(labelFeatures)
        encoded_labels = le.fit_transform(self.ast_features).reshape(-1, 1)

        # x_train, x_test, y_train, y_test = train_test_split(encodedLabels, le.fit_transform(astFeatures),
        # test_size=0.3,
        x_train, x_test, y_train, y_test = train_test_split(encoded_labels, le.fit_transform(self.label_features),
                                                            test_size=0.3,
                                                            random_state=100)

        self.model = self.model.fit(x_train, y_train)

    def predict(self, dataframe):
        prediction = self.model.predict(dataframe)
        logger.info("Accuracy: ", accuracy_score(dataframe, prediction))
        return prediction
