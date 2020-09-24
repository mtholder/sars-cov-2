calc.new.cases <- function(y) {
  curr = y[2:length(y)];
  prev = y[1:length(y) - 1];
  new_cases = curr - prev;
  return(new_cases);
}

mean.over.window <- function(nc, ncwin) {
  tdwnc = c()
  for (i in ncwin:length(nc)) {
    tind = i + 1 - ncwin;
    tdwnc[tind] = 0;
    for (j in 1:ncwin) {
      tdwnc[tind] = tdwnc[tind] + (nc[1 + i - j]/ncwin) ;
    }
  }
  return(tdwnc);
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
singlelagx = x[2:length(x)]
xticks = c(x[1], x[lx/4], x[lx/2], x[3*lx/4], x[lx])

wx = x[(length(x) %% 7) + 1]
while (wx[length(wx)] < x[length(x)]) {
  wx[1 + length(wx)] = wx[length(wx)] + 7
}
prevweekxticks = xticks[2:length(xticks)] - 7
ncwin = 7
lagx = x[(1+ncwin):length(x)]
llagx = length(lagx)
lagxticks = c(lagx[1], lagx[llagx/4], lagx[llagx/2], lagx[3*llagx/4], lagx[llagx])

wnc = calc.new.cases(confirmed$world)
cnc = calc.new.cases(confirmed$mainland.china)
upp.plot.lim.wnc = upper.plot.limit(max(wnc)) # not quite right, but works in p
upp.plot.lim.cnc = upper.plot.limit(max(wnc)) # not quite right, but works in p
upp.nc.plot.lim = max(upp.plot.lim.cnc, upp.plot.lim.wnc)
polyx = c(confirmed$asdate, rev(confirmed$asdate))
for (ry in names(confirmed)) {
  if (ry != "date" && ry != "asdate") {
    country <- gsub("\\.", "-", ry);
    print(country);
    y = confirmed[ry][[1]];
    if (max(y) > 0) {
      dates = confirmed$asdate;
      # number confirmed by time plot for each country 
      pngfn = paste("plots/confirmed/confirmed-", country, ".png", sep="") 
      png(pngfn)
      yticks = c(10E0, 10E1, 10E2, 10E3, 10E4, 10E5, 10E6)
      dy = dead[ry][[1]];
      recy = recovered[ry][[1]];
      plot(confirmed$asdate, y,
           log="y", type='l', 
           ylim=c(1, 2*10E6),
           axes=FALSE, ylab="# confirmed cases", xlab="date", main=country)
      lines(confirmed$asdate, dy, col="red")
      if (recy[length(recy)] > 0) {
        lines(confirmed$asdate, recy, col="blue")
        lines(confirmed$asdate, y - dy - recy, lty=2)
      }
      axis(side=2, at=yticks, labels=yticks)
      axis(side=1, at=wx, labels=wx)
      box()
      abline(v=wx, lty=14, col="grey")
      abline(h=yticks, lty=14, col="grey")
      abline(h=yticks/2, lty=15, col="grey")
      # abline(v=prevweekxticks, lty=15, col="grey")
      dev.off()
      
      nc = calc.new.cases(y)
      tdwnc <- mean.over.window(nc, ncwin)
      dnc = calc.new.cases(dy)
      dwnc <- mean.over.window(dnc, ncwin)
      pncx = confirmed$asdate[(ncwin+1):length(confirmed$asdate)]
      pncnwx = confirmed$asdate[2:length(confirmed$asdate)];
      dualplot = T
      if (dualplot) {
        pngfn = paste("plots/dual-", country, ".png", sep="")
        png(pngfn)
        plot(lagx, tdwnc, type="l", col="black", ylab="mean cases/day")
        abline(h=0)
        par(new=T)
        plot(lagx, dwnc, type="l", col="red", lty=2, col.lab="red", axes=F, xlab=NA, ylab=NA)
        axis(side=4, col="red")
        mtext(side = 4, line = 3, col="red", 'Avg #deaths/day')
        abline(h=0, col="red")
        dev.off()
      } else {
        # daily new case number by time plot for each country 
        pngfn = paste("plots/newcases/newcases-", country, ".png", sep="") 
        png(pngfn)
        barplot(tdwnc, ylab=paste("avg. # new cases/day prev ", ncwin, " days"), xlab="", main=country, names.arg=lagx, las=3)
        dev.off()
  
        pngfn = paste("plots/newcases/newcases-nowindow-", country, ".png", sep="") 
        png(pngfn)
        barplot(nc, ylab=paste("# new cases/day"), xlab="", main=country, names.arg=singlelagx, las=3)
        dev.off()
    
        if (min(nc) < 0) {
          print(paste("negative new case counts in ", country))
        }
        
        pngfn = paste("plots/deaths/newdeaths-", country, ".png", sep="") 
        png(pngfn)
        barplot(dwnc, ylab=paste("avg. # new deaths/day prev ", ncwin, " days"), xlab="", main=country, names.arg=lagx, las=3)
        dev.off()
        pngfn = paste("plots/deaths/newdeaths-nowindow-", country, ".png", sep="") 
        png(pngfn)
        barplot(dnc, ylab=paste("# new deaths/day"), xlab="", main=country, names.arg=singlelagx, las=3)
        dev.off()
        pngfn = paste("plots/newcases/prop-newcases-", country, ".png", sep="") 
        png(pngfn)
        plot(pncx, tdwnc*100 / y[ncwin:(length(y)-1)], type="l",
             ylab=paste("mean ", ncwin, " day window new cases as %"), xlab="date", main=country, ylim=c(0, 50),
             axes=TRUE)
        # lines(pncx, dwnc*100 / dy[ncwin:(length(dy)-1)], col="red")
        abline(h=c(0,10,20,30,40,50), lty=14, col="grey")
        abline(h=c(5,15,25,35,45), lty=15, col="grey")
        dev.off()
        
        pngfn = paste("plots/newcases/prop-newcases-nowindow-", country, ".png", sep="")
        png(pngfn)
        plot(pncnwx, nc*100 / y[1:(length(y)-1)], type="l",
             ylab=paste("mean ", ncwin, " day window new cases as %"), xlab="date", main=country, ylim=c(0, 50),
             axes=TRUE)
        # lines(pncnwx, dnc*100 / dy[ncwin:(length(dy)-1)], col="red")
        abline(h=c(0,10,20,30,40,50), lty=14, col="grey")
        abline(h=c(5,15,25,35,45), lty=15, col="grey")
        dev.off()
      }
    }
  } 
}

