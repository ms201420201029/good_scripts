#install.packages("mlbench")
#library("mlbench")
#install.packages("survival")
library("survival")
library(lattice)
#install.packages("splines")
library(splines)
#install.packages("parallel")
library(parallel)
#install.packages("caret")
#install.packages("gbm")
library("gbm")
#install.packages("pROC")
library(pROC)
library(ggplot2)
library("caret")

############################################GBDT################################################
#setwd("D:/Rworkspace")
data<-read.table("DCA_data.txt",header = TRUE,sep = "\t",check.names = F)
y<-data$y
y<-as.factor(y)
print(y)
#data<-data.frame(lapply(data[,-1],function(x) as.numeric(sub("%","",x))/100))
#data<-cbind(y,data)
print(data)

validation_data<-read.table("validation_data.txt",header = TRUE,sep = "\t",check.names = F)
#validation_data<-data.frame(lapply(validation_data,function(x) as.numeric(sub("%","",x))/100))
#pred.data<-pred.data[1:29,]
print(validation_data)

gbm1 <- 
  gbm(y~.,             # formula  
      data=data,                         # dataset  
      var.monotone=rep(0,12),    # -1: monotone decrease, +1: monotone increase,  
      #  0: no monotone restrictions  
      distribution="bernoulli",        # see the help for other choices  
      n.trees=10,                     # number of trees  
      shrinkage=0.2,                   # shrinkage or learning rate, 0.001 to 0.1 usually work  
      interaction.depth=4,             # 1: additive model, 2: two-way interactions, etc.  
      bag.fraction = 0.8,              # subsampling fraction, 0.5 is probably best  
      train.fraction = 1,           # fraction of data for training, first train.fraction*N used for training  
      n.minobsinnode = 1,             # minimum total weight needed in each node  
      cv.folds = 3,                     # do 3-fold cross-validation  
      keep.data=TRUE,                  # keep a copy of the dataset with the object  
      verbose=FALSE,                   # don't print out progress  
      n.cores=1)                        # use only a single core (detecting #cores is error-prone, so avoided here)  
## check performance using 5-fold cross-validation  
best.iter <- gbm.perf(gbm1,method="cv")  
print(best.iter)  
#plot the performance # plot variable influence  
summary(gbm1,n.trees=best.iter) # based on the estimated best number of trees  
p=predict(gbm1,data,best.iter,type = "response")
p
roc(data$y,p, plot=TRUE, print.thres=TRUE, print.auc=TRUE)  
############################################GBDT################################################
