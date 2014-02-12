library(gplots)
library(RColorBrewer)
library(klaR)
library(corrplot)

d <- read.csv('/tmp/tags.csv')

cl <- kmodes(x, 4)

pts <- jitter(x)
plot(pts, col = cl$cluster)
text(pts, labels=colnames(d))
points(cl$modes, col = 1:5, pch = 8)


df <- t(d)

corrplot(cor(d))
