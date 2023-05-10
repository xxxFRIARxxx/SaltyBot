import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import KernelPCA, PCA
from sklearn.manifold import TSNE
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from matplotlib import pyplot as plt
from SaltyPanda import SaltyPanda
from SaltyDatabase import SaltyDatabase

panda = SaltyPanda()
database = SaltyDatabase()

# ID, p1name, p1odds, p1win, p1streak, p1mu, p1sigma, p1tier, p1tourney, p1time, p2name, 
# p2odds, p2win, p2streak, p2mu, p2sigma, p2tier, p2tourney, p2time, betOutcome

# TODO: Maybe we're missing info about a fighter's first fight? (find out thru sigma mu?)
db = database.db_for_pandas()
dataframe = panda.dataframe(db)
X = dataframe
X = X.drop(["ID", "p1name", "p2name", "p1streak", "p2streak", "p1win", "p2win", "betOutcome"],axis=1)

saltyscalar = StandardScaler()
Xstandardized = saltyscalar.fit_transform(X)

reduceor = KernelPCA(n_components=2,kernel="rbf")
reduced_array = reduceor.fit_transform(Xstandardized)    

# reduceor = PCA()
# tsne = TSNE()
# pca_array = reduceor.fit_transform(Xstandardized)#, dataframe["betOutcome"]) 
# reduced_array = tsne.fit_transform(pca_array)


X_set = reduced_array
Y_set = dataframe["betOutcome"].to_numpy()
labels = np.unique(Y_set)


X1, X2 = np.meshgrid(np.arange(start = X_set[:, 0].min()*1.1, stop = X_set[:, 0].max()*1.1, step = 0.01), np.arange(start = X_set[:, 1].min()*1.1, stop = X_set[:, 1].max()*1.1, step = 0.01))
plt.xlim(X1.min(), X1.max())
plt.ylim(X2.min(), X2.max())

for i,j in enumerate(labels):
    plt.scatter(X_set[Y_set==j,0],X_set[Y_set==j,1],c=["red", "blue"][i],alpha=[1,0.35][i])

plt.show()