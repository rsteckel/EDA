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





my_palette <- colorRampPalette(c("#a50026","#d73027","#f46d43","#fdae61","#fee08b","#ffffbf","#d9ef8b","#a6d96a","#66bd63","#1a9850","#006837"))(n = 10)
heatmap.2(as.matrix(heatdata), Rowv = NA, Colv = NA, scale = "column", col=my_palette, na.rm=TRUE, 
          keep.dendro=FALSE, trace='none', margins=c(10,10), density.info='density')

?heatmap.2


top_coocurrences <- function(heatdata) {
  inds <- which(heatdata > 0, arr.ind=TRUE)
  indices <- data.frame(ind=inds)
  df = data.frame(rowname=rownames(heatdata)[indices$ind.row],
                  colname=colnames(heatdata)[indices$ind.col],
                  counts=heatdata[inds])
  interdf <- df[ df$rowname != df$colname, ]
  interdf[ order(interdf$counts, decreasing=TRUE), ][1:10,]
}


heatdata <- read.csv('/Users/rsteckel/tmp/skin-cooc.csv')
rownames(heatdata) = colnames(heatdata)
heatmap(as.matrix(heatdata))

top_coocurrences(heatdata)



heatdata <- read.csv('/Users/rsteckel/tmp/hair-cooc.csv')
rownames(heatdata) = colnames(heatdata)
heatmap(as.matrix(heatdata))

top_coocurrences(heatdata)



heatdata <- read.csv('/Users/rsteckel/tmp/eye-cooc.csv')
rownames(heatdata) = colnames(heatdata)
heatmap(as.matrix(heatdata))

top_coocurrences(heatdata)

