#! /usr/bin/Rscript

# plot the CW Activity metric for 1-UPPER_BOUND, LOWER_BOUND+

max_y <- 0

args <- commandArgs(trailingOnly=TRUE)

MIN_YEAR <- as.integer(args[1])
MAX_YEAR <- as.integer(args[2])
UPPER_BOUND <- as.integer(args[3])
OUT_DIR <- args[4]

colours <- c('red', 'yellow', 'blue', 'green', 'black', 'white', 'chocolate4', 'darkorchid3', 'hotpink1', 'lightseagreen', 'royalblue2', 'burlywood4')

auto_round <- function(x)
{ lg <- log10(x)
  
  if (lg == as.integer(lg))
  { return (x)
  }
  
  q <- as.integer(lg)
  
  fact <- as.integer(x / (10 ** q)) + 1
  
  return (fact * (10 ** (q)))
}

graphics.off()

factor <- seq(0, 1, length = UPPER_BOUND)
bands <- c('HF', '10', '12', '15', '17', '20', '30', '40', '80', '160')

metric <- data.frame(matrix("", ncol = length(bands), nrow = MAX_YEAR - MIN_YEAR + 1))

names(metric) <- bands

for (band in bands)
{ filename_35 <- paste(sep="", 'exact_appearances_1_', as.character(UPPER_BOUND), '.', band)
  filename_36 <- paste(sep="", 'ge', as.character(UPPER_BOUND+1), '.', band)
 
  d35 <- read.csv(paste(sep="", OUT_DIR, '/', filename_35), header = FALSE)
  d36 <- read.csv(paste(sep="", OUT_DIR, '/', filename_36), header = FALSE)
  d36 <- as.numeric(d36[1,])

  annual_metrics <- vector(mode="numeric", length=MAX_YEAR - MIN_YEAR + 1)
 
  for (year in seq(MIN_YEAR, MAX_YEAR))
  { nr <- year - MIN_YEAR + 1
   
    d <- d35[,nr]
    annual_metrics[nr] <- sum(d * factor) + d36[nr]
  }
 
  metric[,band] <- annual_metrics 
}

ymax <- auto_round(max(metric))
X <- seq(MIN_YEAR, MAX_YEAR)
x_lab <- 'Year'
y_lab <- 'CW Activity Metric'

options(scipen=5)

png(file = paste(sep="", OUT_DIR, '/', 'metric.png'), width = 800, height = 600) 
plot(0, 0, xlim = c(min(X), max(X)), ylim = c(0, ymax), xaxt = "n", yaxt = "n", xlab = x_lab, ylab = y_lab, type = 'n', xaxs="i", yaxs="i")  # define the plotting region, but don't actually plot anything
rect(par("usr")[1], par("usr")[3], par("usr")[2], par("usr")[4], col = "grey") # set the background colour

TITLE <- 'CW ACTIVITY METRIC'
title(TITLE)

x_ticks_at <- X
x_labels_at <- x_ticks_at
x_tick_labels <- x_ticks_at

axis(side = 1, at = x_ticks_at, labels = x_tick_labels )    # ticks on x axis
axis(side = 2)

band_nr <- 0

for (band in bands)
{ band_nr <- band_nr + 1
  Y <- metric[, band]
    
  lines(X, metric[, band], col = colours[band_nr])
  text(x = MIN_YEAR + (MAX_YEAR - MIN_YEAR) * 0.05, y = ymax * 0.95 - ymax * 0.030 * band_nr, labels = band, col = colours[band_nr])
}

# logo
par(new=TRUE)
plot(0, 0, xlim = c(0, 1), ylim = c(0, 1), xaxt = "n", yaxt = "n", type = 'n', xaxs="i", yaxs="i", ann=FALSE)  # define the plotting region, but don't actually plot anything

par(mar = rep(0, 4))    # so we can use the entire area
text(x = 0.9, y = -0.1, labels = c('N7DR'))                                                                                    # title
rect(xl = 0.86, yb = -0.13, xr = 0.94, yt = -0.07, col = NA, lwd = 2)

graphics.off()
 
