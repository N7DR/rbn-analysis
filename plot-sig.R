#!/usr/bin/Rscript

# plot stations's signal

# plot-sig.R call band start-date end-date
# e.g.,
# plot-sig[.R] N7DR 10m 20111126 20111126

# dada examples:
# KT1D-1,K,NA,3504.6,80m,NR4M,K,NA,CQ,35,2009-02-21 00:00:02+00,,,20090221,1235199602
# WA7LNW,K,NA,28239,10m,AL7FS,KL,NA,DX,3,2013-12-12 23:59:59,12,CW,20131212,1386917999

# POSTER, POSTER-COUNTRY-PREFIX, POSTER-CONTINENT, FREQUENCY (kHz), BAND, DX, DX-COUNTRY-PREFIX, DX-CONTINENT, CQ, SNR (dB), DATE-AND-TIME, WPM, MODE, DATE, UNIX-EPOCH

# 0: POSTER
# 1: POSTER-COUNTRY-PREFIX
# 2: POSTER-CONTINENT
# 3: FREQUENCY (kHz)
# 4: BAND
# 5: DX
# 6: DX-COUNTRY-PREFIX
# 7: DX-CONTINENT
# 8: CQ
# 9: SNR (dB)
# 10: DATE-AND-TIME
# 11: WPM
# 12: MODE
# 13: DATE
# 14: UNIX-EPOCH

filename <- "/zfs1/data/rbn/rbndata.csv"  # RBN data file
NBINS <- 200                              # number of discrete time bins
bg_colour <- colours()[342]               # background colour on the plot
colour_scale  <- colorRampPalette(c('green', 'yellow', 'red'))  # colour scale with standard colour shape

continents <- as.factor(c('AF', 'AS', 'EU', 'NA', 'OC', 'SA'))

# read arguments from command line
args <- commandArgs(TRUE)

call <- args[1]
target_band <- args[2]
start <- args[3]
end <- args[4] 

# create version of the call with / replaced by -
safe_call <- gsub("/", "-", call)

# extract pertinent data from the RBN data file
command <- paste(sep="", "grep ',", call, ",' ", filename, " | cut --delimiter=, -f3,5,10,14,15")
column_classes <- c("CHARACTER", "CHARACTER", "INTEGER", "CHARACTER", "INTEGER")

data <- read.csv(pipe(command), na.strings = "")

# make data access more user friendly
names(data) <- c("continent", "band", "snr", "date", "epoch")

# remove data outside the date boundaries
data <- subset(data, ( (date <= end) & (date >= start) ) )

# calculate the limits of the plot
start_date <- as.Date(as.POSIXct(min(data$epoch), tz = "GMT", origin="1970-01-01"))
end_date <- as.Date(as.POSIXct(max(data$epoch), tz = "GMT", origin="1970-01-01"))

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
days <- (x_max - x_min) / 86400

delta_epoch <- x_max - x_min
step <- delta_epoch / NBINS                     # duration of a bin

data$binned <- cut(data$epoch, br = sd_seconds + (step * (0:NBINS)), labels = 1:NBINS)  # add the bin labels

data_list <- list()

# separate the continents
for (this_continent in continents)
{ data_list[[this_continent]] <- subset(subset(data, continent == this_continent ), band == target_band)
}

med_list <- list()
y_max <- 0                # initial value of max SNR

# get the median
get_median <- function(x) 
{ if (length(x) <= 1) return (NA) 

  return (median(x))
}

# get the medians, and the maximum value thereof
for (this_continent in continents)
{ med_list[[this_continent]] <- tapply( data_list[[this_continent]]$snr, data_list[[this_continent]]$binned, get_median )
  y_max <- max(y_max, med_list[[this_continent]], na.rm = TRUE)
}

# round up
function_10 <- function(x) { return ( ( as.integer( (x - 1) / 10) +1 ) * 10 ) }    # function to return next higher integral multiple of 10, unless value is already such a multiple
y_max <- function_10(y_max)

#plot_duration <- 0
n_passes <- 1

# simple one-day plot
#if ( (days == 1) && (plot_duration == 0) )
if ( (days == 1) )
{ x_lab <- 'Hours'
  x_axp <- c(x_min, x_max, days * 24)
  x_ticks_at <- seq(0, days * 8) * 3600 * 3 + x_min
  x_tick_labels <- 3 * seq(0, length(x_ticks_at) - 1)     
  x_labels_at <- x_ticks_at
}

# weekend plot
#if ( (days > 1.1) && (days <= 27) && (plot_duration == 0) )
if ( (days > 1.1) && (days <= 27) )
{ x_lab <- 'Hours'
  x_axp <- c(x_min, x_max, days * 24)
  x_ticks_at <- seq(0, days * 4) * 3600 * 6 + x_min
  x_tick_labels <- 6 * seq(0, length(x_ticks_at) - 1)     
  x_labels_at <- x_ticks_at
}

# one-month plot
if ( (days > 7) && (days <= 360) )
{ x_lab <- 'Days'
  x_axp <- c(x_min, x_max, days)
  x_ticks_at <- seq(0, days) * 3600 * 24 + x_min
  x_tick_labels <- c(seq(1, days), "")
  x_labels_at <- x_ticks_at + (3600 * 12)
  n_passes <- 2                                               # offset every other day
}

# one-year plot
if ( (days > 360) && (days < 370) )
{ x_lab <- 'Months'
  x_axp <- c(x_min, x_max, 12)
  x_ticks_at <- c(0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365) * 3600 * 24 + x_min
  x_tick_labels <- c(seq(1, 12), "")
  x_labels_at <- x_ticks_at + (15 * 3600 * 24)
} 

# multi-year plot
if (days >= 370)
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

graphics.off()

png(filename=paste(sep="", safe_call, "-", target_band, "-", start, "-", end, "-by-continent.png"),  width=800, height=600)

# define two screens: one for the plot, one for the legend
screen_1 <- c(0.0, 0.9, 0.0, 1.0)
screen_2 <- c(0.9, 1.0, 0.0, 1.0)

screen_numbers <- split.screen(matrix( c(screen_1, screen_2), byrow = T, ncol = 4))  # we don't actually use the return value, but the assignment stops it from being printed

# the main plot
screen(1)

y_min <- 0

plot(0, 0, type = 'n', xlim = c(x_min, x_max), ylim = c(0, 1), xaxt = "n", yaxt = "n", xlab = x_lab, ylab = '', main = '')  # define the plotting region, but don't actually plot anything

rect(par("usr")[1], par("usr")[3], par("usr")[2], par("usr")[4], col = bg_colour)  # set the background colour

par(new=TRUE)

title_str <- paste(sep="", call, ": ", target_band)
title_str <- paste(sep="", title_str, " ", start, " to ", end)
title(title_str)

axis(side = 1, at = x_ticks_at, labels = FALSE )    # ticks on x axis

if (n_passes == 1)
{ axis(side = 1, at = x_labels_at, labels = x_tick_labels, tick = FALSE ) 
} else
{ axis(side = 1, at = x_labels_at[c(TRUE, FALSE)], labels = x_tick_labels[c(TRUE, FALSE)], tick = FALSE )
  axis(side = 1, at = x_labels_at[c(FALSE, TRUE)], labels = x_tick_labels[c(FALSE, TRUE)], padj = 0.5, tick = FALSE )
}

y_ticks_at <- vector()
for (nc in 1:length(continents))
{ y_ticks_at <- append(y_ticks_at, 1 - ((nc - 0.5 ) * 1 / (length(continents))))
}

axis(side = 2, at = y_ticks_at, labels = continents, las = 1, lwd = 0, lwd.ticks = 1 )

cs <- colour_scale(y_max)  # normalise the colour scale

# plot the data
for (nc in 1:length(continents))
{ par(new=TRUE)

  for (n in (1:NBINS))
  { xleft <- x_min + (n * (x_max - x_min) / NBINS)
    xright <- xleft + (x_max - x_min) / NBINS
    ybottom <- 1 - (nc / length(continents))
    ytop <- ybottom + 1 / length(continents)
    
    rect(xleft, ybottom, xright, ytop, col = cs[med_list[[nc]][n]], border = NA)
  }
}

# display the gradient  
screen(2)

par(mar = rep(0, 4))    # so we can use the entire area

plot(c(0,2), c(0, 1), type = 'n', axes = F, xlab = '', ylab = '', main = '')  # define the plotting region, but don't actually plot anything

text(x=1.5, y = seq(0.1, 0.9, l = ((y_max / 10) + 1)), labels = seq(0 , y_max, l = ((y_max / 10) + 1)) )  # legend 
text(x= 0.5, y = 0.925, labels = c('dB'))                                                                                    # title

legend_image <- as.raster(matrix(colour_scale(y_max), ncol = 1))
rasterImage(legend_image, 0.9, 0.9, 0.1, 0.1, angle = 0)                     # parameters cause the gradient to appear in the correct direction

graphics.off()   # close the device and go home
