#!/usr/bin/Rscript

# generate comparison plots of a station's signal as compared to those of all other
# stations on the same continent

# rank-sig.R call band continent start-date end-date [start-hour duration in hours]
# e.g.,
# rank-sig[.R] N7DR 10m EU 20111126 20111126 14 3
  
  TOP_SNR <- 40    # upper limit of graph will be at least this value of SNR
  TOP_COUNT <- 20  # colour gradient will go up to at least this value
  GAP_SIZE <- 2000 # number of seconds that represents a data gap
  
# read the arguments from the command line
  args <- commandArgs(TRUE)
  
  call <- args[1]
  band <- args[2]
  continent <- args[3]
  start <- args[4]
  end <- args[5]
  
  start_hour <- 0
  plot_duration <- 0
  
  if (length(args) == 7)
  { start_hour <- as.integer(args[6])
    plot_duration <- as.integer(args[7])
  }
  
  # create version of the call with / replaced by -
  safe_call <- gsub("/", "-", call)
  
# turn off default graphics device
  graphics.off()
  
# obtain start and end dates as seconds w.r.t. the UNIX epoch
  sd <- as.Date(max(c(start, "20090101")), format='%Y%m%d', usetz=false, tz="GMT") # force bound
  posix_sd <- as.POSIXct(sd)
  sd_seconds <- as.numeric(posix_sd)
   
  ed <- as.Date(min(c(end, "20201231")), format='%Y%m%d', usetz=false, tz="GMT")   # force bound
  posix_ed <- as.POSIXct(ed) 
  ed_seconds <- as.numeric(posix_ed)
  
# the actual end is one day later than the start of the end date
  ed_seconds <- ed_seconds + (3600 * 24)
  posix_ed <- as.POSIXct(ed)  

# the x limits for the plots
  x_min <- sd_seconds
  x_max <- ed_seconds
  
# duration of the plot, in days
  domain <- (x_max - x_min) / 86400 #
  
# read the file that was created by the python script rank-sig.R
  filename <- paste(sep="", safe_call, "-", band, "-", continent, "-", start, "-", end, ".rank_data")
  
  fc <- file(filename)
  mylist <- strsplit(readLines(fc), " ")
  close(fc)

# quit if there were no data
  if (length(mylist) == 0)
  { stop("No data")
  }
  
 # convert all the received data to numbers
  mylist <- lapply(mylist, as.numeric)
 
  x_vals <- sapply(mylist, function(x) x[1])  # the UNIX epoch of all the observations
  my_snr <- sapply(mylist, function(x) x[2])  # the SNR of the target station at the respective epochs
 
# create several vectors that will hold data for calculations and plotting
  x <- vector()               # UNIX epoch, with each epoch repeated as necessary to match number of measurements
  y <- vector()               # SNR values of stations other than the target 
  x_new <- vector()           # UNIX epoch, with each epoch repeated as necessary to match number of *different* SNR measurements 
  y_new <- vector()           # observed values of SNR (not including target's SNR)
  count <- vector()           # total count of matching posts at a particular epoch
  my_rank <- vector()         # target's rank at a particular epoch (with 1 == *lowest* signal, which is R's behaviour)
  n_values <- vector()        # number of values at an epoch (including target's value)
  max_snr_value <- vector()   # maximum SNR recorded at a particular time (not including target SNR)
 
  function_all_snrs <- function(x, y) { return (x[y:length(x)]) }    # function to return subset of SNR values at a particular epoch

  all_list <- lapply(mylist, function_all_snrs, 2)                   # ALL the SNRs (including target's) at each epoch
  other_snrs <- lapply(mylist, function_all_snrs, 3)                 # all the SNRs except target's at each epoch
 
  df_list <- list()                                                  # list of data frames
 
  for (n in 1:length(x_vals))                                                                  # for each epoch
  { x <- append(x, seq(x_vals[n], x_vals[n], length.out = length(other_snrs[[n]])))            # epoch, repeated the number of times needed to match the number of observations at that time
    y <- append(y, other_snrs[[n]])                                                            # add all the other SNR values at this epoch
   
    my_rank <- append(my_rank, rank(all_list[[n]])[1])                                         # rank of first element (which is the target)
    n_values <- append(n_values, length(all_list[[n]]))                                        # number of different SNR values
    max_snr_value <- append(max_snr_value, max(c(max(other_snrs[[n]]), TOP_SNR), na.rm=TRUE))  # maximum SNR at an epoch (or TOP_SNR)

# generate a data frame containing the count of each value at this epoch
# http://stackoverflow.com/questions/1923273/counting-the-number-of-elements-with-the-values-of-x-in-a-vector
    tdf <- as.data.frame( table(other_snrs[[n]]) )
    colnames(tdf) <- c("snr_value","snr_count")   # friendly names; at this point, snr_value contains levels

# http://stackoverflow.com/questions/9480408/convert-factor-to-integer-in-a-data-frame  
    tdf$snr_value <- as.numeric( as.character(tdf$snr_value) )    # convert levels to the original integers NB the as.character function is necessary, otherwise the numeric is applied to the level value
   
    df_list[[n]] <- tdf                                           # add to the list
   
    n_different_values <- length(tdf$snr_value)                   # number of different SNR values
    x_new <- append(x_new, seq(x_vals[n], x_vals[n], length.out = n_different_values))  # epoch, repeated the number of times needed to match the number of *different* observations at that time
    y_new <- append(y_new, tdf$snr_value)                         # the different SNR values
    count <- append(count, tdf$snr_count)                         # count of different SNR values at this epoch
  }
 
  function_10 <- function(x) { return ( ( as.integer( (x - 1) / 10) +1 ) * 10 ) }    # function to return next higher integral multiple of 10, unless value is already such a multiple
 
  max_count <- max( max(count, na.rm=TRUE), TOP_COUNT)            # highest value of count
  max_count_10 <- function_10(max_count)                          # rounded
  
  global_max_snr_value <- max(max_snr_value, na.rm=TRUE)          # highest value of SNR
  global_max_snr_value_10 <- function_10(global_max_snr_value)    # rounded
  
# generate a colour scale with standard colour shape
  colour_scale  <- colorRampPalette(c('green', 'yellow', 'red'))
 
  pc <- my_rank / n_values * 100                                  # percentile
 
# generate parameters for different durations of plot

  n_passes <- 1                      # default number of passes for writing x labels
  
# simple one-day plot
  if ( (domain == 1) && (plot_duration == 0) )
  { x_lab <- 'Hours'
    x_axp <- c(x_min, x_max, domain * 24)
    x_ticks_at <- seq(0, domain * 8) * 3600 * 3 + x_min
    x_tick_labels <- 3 * seq(0, length(x_ticks_at) - 1)     
    x_labels_at <- x_ticks_at
  }
 
# plot with start and duration specified explicitly on the command line
  if (plot_duration != 0) 
  { x_lab <- 'Hours'
    x_min <- x_min + start_hour * 3600
    x_max <- x_min + plot_duration * 3600
    x_axp <- c(x_min, x_max, plot_duration)  # one-hour ticks
    x_ticks_at <- seq(0, plot_duration) * 3600 + x_min
   
    x_tick_labels <- start_hour + seq(0, length(x_ticks_at) - 1)  
    x_tick_labels <- x_tick_labels %% 24
   
    if (x_tick_labels[length(x_tick_labels)] == 0)
      x_tick_labels[length(x_tick_labels)] <- 24    # if we end at the end of a day, call it 24, not 0
   
    x_labels_at <- x_ticks_at   
  } 
 
# weekend plot
  if ( (domain > 1.1) && (domain <= 27) && (plot_duration == 0) )
  { x_lab <- 'Hours'
    x_axp <- c(x_min, x_max, domain * 24)
    x_ticks_at <- seq(0, domain * 4) * 3600 * 6 + x_min
    x_tick_labels <- 6 * seq(0, length(x_ticks_at) - 1)     
    x_labels_at <- x_ticks_at
  }
 
# one-month plot
  if ( (domain > 27) && (domain <= 360) )
  { x_lab <- 'Days'
    x_axp <- c(x_min, x_max, domain)
    x_ticks_at <- seq(0, domain) * 3600 * 24 + x_min
    x_tick_labels <- c(seq(1, domain), "")
    x_labels_at <- x_ticks_at + (3600 * 12)
    n_passes <- 2                                               # offset every other day
  }
 
# one-year plot
  if ( (domain > 360) && (domain < 370) )
  { x_lab <- 'Months'
    x_axp <- c(x_min, x_max, 12)
    x_ticks_at <- c(0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365) * 3600 * 24 + x_min
    x_tick_labels <- c(seq(1, 12), "")
    x_labels_at <- x_ticks_at + (15 * 3600 * 24)
  } 

# multi-year plot
  if (domain >= 370)
  { x_lab <- 'Years'
    start_year_str <- substring(start, 1, 4)
    end_year_str <- substring(end, 1, 4)
    start_year <- as.integer(start_year_str)
    end_year <- as.integer(end_year_str)
    x_axp <- c(x_min, x_max, end_year - start_year + 1 )
    x_ticks_at <- seq(0, end_year - start_year + 1) * 365 * 3600 * 24 + x_min
    x_tick_labels <- c(start_year + seq(0, end_year - start_year), "")
    x_labels_at <- x_ticks_at + (365 * 3600 * 24 / 2)
  }
  
# create the graphics device
  png(filename=paste(sep="", safe_call, "-", band, "-", continent, "-", start, "-", end, ".png"), width=800, height=1200)

# split into four screens:
# 1: the main plot
# 2: the gradient
# 3: the percentile plot
# 4: unused (but could be used for a legend for different calls)

  screen_1 <- c(0, 0.9, 0.5, 1)
  screen_2 <- c(0.9, 1, 0.5, 1)
  screen_3 <- c(0, 0.9, 0, 0.5)
  screen_4 <- c(0.9, 1, 0, 0.5)
  
  screen_numbers <- split.screen(matrix( c(screen_1, screen_2, screen_3, screen_4), byrow = T, ncol = 4))  # we don't actually use the return value, but the assignment stops it from being printed
  
# the main plot
  screen(1)
 
  title_str <- paste(sep="", call, ": ", band, " ", continent)

  s_hour <- as.character(start_hour)
  if (start_hour < 10)
  { s_hour <- paste(sep="", "0", s_hour)
  }

  if ( plot_duration != 0)
  { title_str <- paste(sep="", title_str, " start at ", start, " ", s_hour, "00z")
  } else 
  { title_str <- paste(sep="", title_str, " ", start, " to ", end)
  }
 
  title(title_str)
 
  rect(par("usr")[1], par("usr")[3], par("usr")[2], par("usr")[4], col = "blue")  # set the background colout
  par(new=TRUE)

  plot (x_new, y_new, xlim = c(x_min, x_max), xaxp = x_axp, xaxt = "n", , xlab = x_lab, ylim = c(0, global_max_snr_value_10), ylab = '(S+N)/N (dB)', pch = 15, col = colour_scale(max_count_10)[count])

  axis(side = 1, at = x_ticks_at, labels = FALSE )    # ticks on x axis
  
  if (n_passes == 1)
  { axis(side = 1, at = x_labels_at, labels = x_tick_labels, tick = FALSE ) 
  } else
  { axis(side = 1, at = x_labels_at[c(TRUE, FALSE)], labels = x_tick_labels[c(TRUE, FALSE)], tick = FALSE )
    axis(side = 1, at = x_labels_at[c(FALSE, TRUE)], labels = x_tick_labels[c(FALSE, TRUE)], padj = 0.5, tick = FALSE )
  }
 
  points(x_vals, my_snr, col='red')  # mark the target's SNR values

# function to return x and y with data gaps wherever a gap of d seconds occurs
  function_engap <- function(x, y, d) 
  { gap <- which( diff(x) > d )
  
    if (length(gap))
    { newx <- (x[gap] + x[gap+1]) / 2
      x <- c(x, newx)
      y <- c(y, rep(NA, length(newx)))

      o <- order(x)
      return (list(x[o], y[o]))
    } else
    { return (list(x, y))   # no gaps
    }
  }

  line_vals <- function_engap(x_vals, my_snr, GAP_SIZE)
 
  lines(line_vals[[1]], line_vals[[2]], lwd = 3, col='red')  # draw the lines (with gaps)

# display the gradient  
  screen(2)
 
  par(mar = rep(0, 4))    # so we can use the entire area
 
  plot(c(0,2), c(0, 1), type = 'n', axes = F, xlab = '', ylab = '', main = '')  # define the plotting region, but don't actually plot anything
 
  text(x=1.5, y = seq(0.1, 0.9, l = ((max_count_10 / 10) + 1)), labels = seq(0 , max_count_10, l = ((max_count_10 / 10) + 1)) )  # legend 
  text(x= 0.5, y = 0.95, labels = c('Posts'))                                                                                    # title
 
  legend_image <- as.raster(matrix(colour_scale(max_count_10), ncol = 1))
  rasterImage(legend_image, 0.9, 0.9, 0.1, 0.1, angle = 0)                     # parameters cause the gradient to appear in the correct direction
 
# the percentile plot
  screen(3)
 
  line_vals <- function_engap(x_vals, pc, GAP_SIZE)                            # put gaps in the data as necessary
 
  plot (line_vals[[1]], line_vals[[2]], type='l', lwd = 2, xlim = c(x_min, x_max), xaxp = x_axp, xaxt = "n", , xlab = x_lab, ylim = c(0, 100), ylab = '(S+N)/N percentile', pch = 15, col = 'red')

  title(title_str)
 
  axis(side = 1, at = x_ticks_at, labels = FALSE )
  if (n_passes == 1)
  { axis(side = 1, at = x_labels_at, labels = x_tick_labels, tick = FALSE ) 
  } else
  { axis(side = 1, at = x_labels_at[c(TRUE, FALSE)], labels = x_tick_labels[c(TRUE, FALSE)], tick = FALSE )
    axis(side = 1, at = x_labels_at[c(FALSE, TRUE)], labels = x_tick_labels[c(FALSE, TRUE)], padj = 0.5, tick = FALSE )
  }
 
# we're done; close the device and go home 
 graphics.off()
  