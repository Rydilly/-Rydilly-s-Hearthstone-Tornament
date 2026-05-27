import numpy
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss, accuracy_score
import pickle

def train(in_name:str,out_name:str):
    #Load
    d = numpy.load(in_name)
    X=d["X"]
    Y=d["Y"]
    print(f"Loaded {len(X)} samples")

    #Sort
    data_len = int(len(X)*.8)
    X_train,X_test,Y_train,Y_test= train_test_split(
        X,Y,test_size=.02,random_state=0#shuffle before splitting
        )

    #Train
    model = LogisticRegression(max_iter=2000)
    model.fit(X_train,Y_train)

    #Eval
    train_probs = model.predict_proba(X_train)[:,1]#2nd column is win rating first is loss rating
    test_probs = model.predict_proba(X_test)[:,1]

    print(f"Train log_loss: {log_loss(Y_train,train_probs):.4f}")#log_loss is a decimal between 0 and 1 the closer it is to the actual result 0 or 1 the less "wrong it is"
    print(f"Test log_loss: {log_loss(Y_test,test_probs):.4f}")#since log_loss scales it takes log(confidence its right). this makes the midpoint or 50/50 .693 (hehe 69)
    #using log loss because the trainer should be more surprised from being super wrong then supper right to ensure it fits all possible variations
    #if you are a weather man saying 90% chance of rain vs 95% isnt much of a difference, but if it dosnt rain you should be shocked and adjust something


    print(f"Train Accuracy: {accuracy_score(Y_train,train_probs>.5)}")#if log_loss is closer to actual prob it will inc the count
    print(f"Test Accuracy: {accuracy_score(Y_test,test_probs>.5)}")

    #save
    with open(out_name,"wb") as f:
        pickle.dump(model,f)
    print("Saved model!")

if __name__=="__main__":
    in_file = "training-data-test.npz"
    out_file = "model-test.pkl"
    train(in_file,out_file)


