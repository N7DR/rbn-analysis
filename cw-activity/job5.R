#! /usr/bin/Rscript

# plot the graphs of number of posts in range 1..100 for each band

# params: MIN_YEAR MAX_YEAR OUT_DIR

args <- commandArgs(trailingOnly=TRUE)

MIN_YEAR <- as.integer(args[1])
MAX_YEAR <- as.integer(args[2])
OUT_DIR <- args[3]

bands <- c('HF', '160', '80', '40', '30', '20', '17', '15', '12', '10')

auto_round <- function(x)
{ lg <- log10(x)
  
  if (lg == as.integer(lg))
  { return (x)
  }
  
  q <- as.integer(lg)
  
  fact <- as.integer(x / (10 ** q)) + 1
  
  return (fact * (10 ** (q)))
}

min_0  <- function(x)
  { return (max(x, 0)) }

for (band in bands)
{ filename <- paste(sep ="", OUT_DIR, '/', 'exact_appearances_1_100.', as.character(band))

  colours <- c('red', 'yellow', 'blue', 'green', 'black', 'white', 
               'chocolate4', 'darkorchid3', 'hotpink1', 'lightseagreen', 'royalblue2', 'burlywood4')



  d <- read.csv(filename, header = FALSE)                        # this produces a data /frame/, despite the name
  d <- log10(d)

  png(file = paste(sep="", OUT_DIR, '/', 'log_n_appearances.', as.character(band), '.png'), width = 800, height = 600) 

  ymax <- auto_round(max(d))

  years <- seq(MIN_YEAR, MAX_YEAR)

  min_year <- min(years)

  x_lab <- 'Number of Appearances (n)'
  y_lab <- 'Log(Number of calls) (Log(V(n)))'

  appearances <- seq(1, 100)

  min_appearances <- min(appearances)
  max_appearances <- max(appearances)

  plot(0, 0, xlim = c(0, max_appearances), ylim = c(0, ymax), xaxt = "n", yaxt = "n", xlab = x_lab, ylab = y_lab, type = 'n', xaxs="i", yaxs="i")  # define the plotting region, but don't actually plot anything
  rect(par("usr")[1], par("usr")[3], par("usr")[2], par("usr")[4], col = "grey") # set the background colour

  suffix <- ifelse(band == 'HF', '', 'm')

  title_str <- paste(sep="", 'LOG(N(CALLS)) v. NUMBER OF APPEARANCES [LOG(V(n))] -- ', as.character(band), suffix)
  title(title_str)

  x_ticks_at <- seq(0, max_appearances, by = 10)
  x_labels_at <- x_ticks_at
  x_tick_labels <- x_ticks_at

  axis(side = 1, at = x_ticks_at, labels = x_tick_labels )    # ticks on x axis
  axis(side=2)

  for (year in years)
  { nr <- year - min_year + 1
    Y <- d[, nr]
    lines( seq(1, 100), Y, col = colours[nr] )
    text(x = 90, y = ymax * 0.9 - ymax * 0.030 * nr, labels = year, col = colours[nr])
  }

# logo
  par(new=TRUE)
  plot(0, 0, xlim = c(0, 1), ylim = c(0, 1), xaxt = "n", yaxt = "n", type = 'n', xaxs="i", yaxs="i", ann=FALSE)  # define the plotting region, but don't actually plot anything

  par(mar = rep(0, 4))    # so we can use the entire area
  text(x = 0.9, y = -0.1, labels = c('N7DR'))                                                                                    # title
  rect(xl = 0.86, yb = -0.13, xr = 0.94, yt = -0.07, col = NA, lwd = 2)

  dev.off()
}
