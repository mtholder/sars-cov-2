confirmed <- read.csv("confirmed.csv", strip.white=TRUE)
confirmed$asdate = as.Date(confirmed$date, format="%m/%d/%Y")
x = confirmed$asdate
lx = length(x)
xticks = c(x[1], x[lx/4], x[lx/2], x[3*lx/4], x[length(x)])
for (ry in names(confirmed)) {
  if (ry != "date" && ry != "asdate") {
    country <- gsub("\\.", "-", ry);
    y = confirmed[ry][[1]];
    if (max(y) > 0) {
      pngfn = paste("plots/confirmed-", country, ".png", sep="") 
      png(pngfn)
      yticks = c(10E0, 10E1, 10E2, 10E3, 10E4, 10E5)
      plot(confirmed$asdate, y,
           log="y", type='l', 
           ylim=c(1, 10E6),
           axes=FALSE, ylab="# confirmed cases", xlab="date", main=country)
      axis(side=2, at=yticks, labels=yticks)
      axis(side=1, at=xticks, labels=xticks)
      box()
      abline(v=xticks, lty=14, col="grey")
      abline(h=yticks, lty=14, col="grey")
      dev.off()
    }
  } 
}

