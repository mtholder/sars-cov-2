calc.new.cases <- function(y) {
  curr = y[2:length(y)];
  prev = y[1:length(y) - 1];
  new_cases = curr - prev;
  return(new_cases);
}

upper.plot.limit <- function(v) {
  # Returns v rounded up at the second most significant digit (base 10)
  z = v - 10**(floor(log10(v)));
  return(ceiling(10**(log10(z) %% 1)) * (10**(floor(log10(z)))) + 10**(floor(log10(v))));
}

confirmed <- read.csv("confirmed.csv", strip.white=TRUE)
dead <- read.csv("dead.csv", strip.white=TRUE)
recovered <- read.csv("recovered.csv", strip.white=TRUE)
confirmed$asdate = as.Date(confirmed$date, format="%m/%d/%Y")
x = confirmed$asdate
lx = length(x)
xticks = c(x[1], x[lx/4], x[lx/2], x[3*lx/4], x[lx])
ncwin = 2
lagx = x[(1+ncwin):length(x)]
llagx = length(lagx)
lagxticks = c(lagx[1], lagx[llagx/4], lagx[llagx/2], lagx[3*llagx/4], lagx[llagx])

wnc = calc.new.cases(confirmed$world)
cnc = calc.new.cases(confirmed$mainland.china)
upp.plot.lim.wnc = upper.plot.limit(max(wnc)) # not quite right, but works in p
upp.plot.lim.cnc = upper.plot.limit(max(wnc)) # not quite right, but works in p
upp.nc.plot.lim = max(upp.plot.lim.cnc, upp.plot.lim.wnc)

for (ry in names(confirmed)) {
  if (ry != "date" && ry != "asdate") {
    country <- gsub("\\.", "-", ry);
    y = confirmed[ry][[1]];
    if (max(y) > 0) {
      dates = confirmed$asdate;
      # number confirmed by time plot for each country 
      pngfn = paste("plots/confirmed/confirmed-", country, ".png", sep="") 
      png(pngfn)
      yticks = c(10E0, 10E1, 10E2, 10E3, 10E4, 10E5)
      dy = dead[ry][[1]];
      recy = recovered[ry][[1]];
      plot(confirmed$asdate, y,
           log="y", type='l', 
           ylim=c(1, 2*10E5),
           axes=FALSE, ylab="# confirmed cases", xlab="date", main=country)
      lines(confirmed$asdate, dy, col="red")
      lines(confirmed$asdate, recy, col="blue")
      lines(confirmed$asdate, y - dy - recy, lty=2)
      axis(side=2, at=yticks, labels=yticks)
      axis(side=1, at=xticks, labels=xticks)
      box()
      abline(v=xticks, lty=14, col="grey")
      abline(h=yticks, lty=14, col="grey")
      dev.off()
      
      # daily new case number by time plot for each country 
      pngfn = paste("plots/newcases/newcases-", country, ".png", sep="") 
      png(pngfn)
      # yticks = c(10E0, 10E1, 10E2, 10E3, 10E4, 10E5)
      nc = calc.new.cases(y)
      tdwnc = c()
      for (i in ncwin:length(nc)) {
        tind = i + 1 - ncwin;
        tdwnc[tind] = 0;
        for (j in 1:ncwin) {
          tdwnc[tind] = tdwnc[tind] + (nc[1 + i - j]/ncwin) ;
        }
      }
      barplot(tdwnc, ylab=paste("avg. # new cases prev ", ncwin, " days"), xlab="", main=country, names.arg=lagx, las=3)
      dev.off()
      if (min(nc) < 0) {
        print(paste("negative new case counts in ", country))
      }
    }
  } 
}



