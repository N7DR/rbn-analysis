#!/usr/bin/Rscript

# generate comparison plot of two stations' signals

# compare-sigs.R call1 call2 band continent start-date end-date
# e.g.,
# compare-sigs[.R] N7DR K7KU 10m EU 20111126 20111126

  MIN_DATA_POINTS <- 10  # minimum number of data points before we have enough data for an analysis of the mean

# read arguments from command line
  args <- commandArgs(TRUE)
  
  call1 <- args[1]
  call2 <- args[2]
  band <- args[3]
  continent <- args[4]
  start <- args[5]
  end <- args[6]  

# create versions of the calls with / replaced by -
  safe_call1 <- gsub("/", "-", call1)
  safe_call2 <- gsub("/", "-", call2)
  
  # turn off default graphics device
  graphics.off()
  
# read data from the file produced by compare-sigs.py
  d <- read.table(paste(sep="", safe_call1, "-", safe_call2, "-", band, "-", continent, "-", start, "-", end, ".data"))
  
# make data access more user friendly
  names(d) <- c("dB")
  attach(d)
  dB <- as.numeric(dB)

# calculate minimum and maximum for plotting purposes
  x0 <- min(dB)
  x1 <- max(dB)
  
  x0 <- ((x0 - 5) / 5) * 5
  x1 <- ((x1 + 5) / 5) * 5
  
# open the graphics device
  png(filename=paste(sep="", safe_call1, "-", safe_call2, "-", band, "-", continent, "-", start, "-", end, ".png"), width=800, height=600)
  
# plot a histogram of the data
  hist(dB, seq(from = x0, to = x1, by = 1) - 0.5, col='red', xlim=c(x0, x1), xlab='dB', ylab='Number of events', main='')
 
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

# plot the µ and standard error information
  height <- yrange / 20
  
  if (length(dB) >= MIN_DATA_POINTS) 
  { 
 # because we don't know the actual variance of the difference distribution, we use the t distribution  
    sample_size <- length(dB)
    df <- sample_size - 1
    factor <- qt(c(0.975, 0.995), df)    # 95% and 99% two-tailed quantile
  
# calculate statistical metrics, assuming that the CLT is applicable
    mu <- mean(dB)
    stdev <- sd(dB)
    se <- stdev / sqrt(sample_size)    # standard error of the mean
  
    dual_factor <- outer(factor, c(-1, 1), FUN="*")  # both tails
    bounds <- mu + (dual_factor * se)                # confidence limits (95% and 99%) when the underlying variance is not known
  
# probability that one station is really stronger than the other, given the sample distribution of differences
    pright <- pt(0, df, mu, lower.tail = FALSE)
  
# convert some numbers to printable strings
    bounds_str <- formatC(bounds, digits=1, format="f")  # confidence limits
    mu_str <- formatC(mu, digits=1, format="f")          # mean
    pright_str <- formatC(pright, digits=2, format="f")  # probability one stn is stronger than the other
    
    rect(bounds[,1], c(0, 0), bounds[,2], c( height, height / 2), col = c('dodgerblue', 'blue4'))  # plot 95% and 99% confidence bars
    lines(c(mu, mu), c(0, height * 1.5), lwd = 3, col = 'green')
  }
  
# size the outer margins, so we have room for the statistical information
  par(xpd = NA, oma = c(5, 2, 2, 2) + 0.1)
   
# generate a string containing the statistical info, ready for printing (although this more or less duplicates the info on the plot, so maybe it's not necessary)
 legend95 <- paste(sep="", "95% confidence = ", bounds_str[1, 1], " to ", bounds_str[1, 2], " dB; µ = ", mu_str, " dB; probability ", call2, " is the stronger = ", pright_str)
  
# uncomment the next line to print statistical information as text
#  if (length(dB) >= MIN_DATA_POINTS) mtext(legend95, side = 1, line = 4, outer=TRUE, col = 'black')

# we're done; close the device and exit
  graphics.off()

  