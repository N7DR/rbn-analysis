#!/usr/bin/Rscript

# generate comparison plot of two stations' signals

# compare-sigs.R call1 call2 band continent start-date end-date
# e.g.,
# compare-sigs[.R] N7DR K7KU 10m EU 20111126 20111126

  MIN_DATA_POINTS <- 30  # minimum number of data points before we have enough data for an analysis of the mean

# read arguments from command line
  args <- commandArgs(TRUE)
  
  call1 <- args[1]
  call2 <- args[2]
  band <- args[3]
  continent <- args[4]
  start <- args[5]
  end <- args[6]
  
  # turn off default graphics device
  graphics.off()
  
# read data from the file produced by compare-sigs.py
  d <- read.table(paste(sep="", call1, "-", call2, "-", band, "-", continent, "-", start, "-", end, ".data"))
  
# make data access more user friendly
  names(d) <- c("dB")
  attach(d)
  dB <- as.numeric(dB)
  
# calculate statistical metrics, assuming that the CLT is applicable
  mu <- mean(dB)
  stdev <- sd(dB)
  se <- stdev / sqrt(length(dB))    # standard error of the mean
  
  lb <- mu - 1.96 * se              # 95% confidence limits
  ub <- mu + 1.96 * se
  
# probability that one station is really stronger than the other, given the sample distribution of differences
  pright <- pnorm(0, mean=mu, sd=se, lower.tail = FALSE)
  
# convert some numbers to printable strings
  lb_str <- formatC(lb, digits=1, format="f") 
  ub_str <- formatC(ub, digits=1, format="f") 
  mu_str <- formatC(mu, digits=1, format="f") 
  
  pright_str <- formatC(pright, digits=2, format="f")
  
# calculate minimum and maximum for plotting purposes
  x0 <- min(dB)
  x1 <- max(dB)
  
  x0 <- ((x0 - 5) / 5) * 5
  x1 <- ((x1 + 5) / 5) * 5
  
# open the graphics device
  png(filename=paste(sep="", call1, "-", call2, "-", band, "-", continent, "-", start, "-", end, ".png"), width=800, height=600)
  
# plot a histogram of the data
  hist(dB, breaks=(x1 - x0) / 2, col='red', xlim=c(x0, x1), xlab='dB', ylab='Number of events', main='')
  
# title
  title_str <- paste(sep="", call2, " wrt ", call1, ": ", band, " ", continent)  
  if (start != "00000000" || end != "30000000") title_str <- paste(sep="", title_str, " ", start, " to ", end) 
  title(title_str) 

# set bounding box for plot
  minx <- par("usr")[1]
  maxx <- par("usr")[2]
  miny <- par("usr")[3]
  maxy <- par("usr")[4]

  xrange <- maxx - minx
  yrange <- maxy - miny

  xpos <- minx + 0.05 * xrange
  ypos <- miny - 0.11 * yrange
  
# size the outer margins, so we have room for the statistical information
  par(xpd = NA, oma = c(5, 2, 2, 2) + 0.1)
   
# generate a string containing the statistical info, ready for printing
 legend95 <- paste(sep="", "95% confidence = ", lb_str, " to ", ub_str, " dB; µ = ", mu_str, " dB; probability ", call2, " is the stronger = ", pright_str)
  
# print it if the Central Limit Theorm is reasonably in effect
  if (length(dB) >= MIN_DATA_POINTS) mtext(legend95, side = 1, line = 4, outer=TRUE, col = 'black')

# we're done; close the device and exit
  graphics.off()

  