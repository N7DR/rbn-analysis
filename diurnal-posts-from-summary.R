#!/usr/bin/Rscript

# generate a plot of the diurnal number of posts by the RBN, stacked by year

MIN_YEAR <- 2009
MAX_YEAR <- 2016

filename <- "/zfs1/data/rbn/rbn-summary-data"  # the local location of the RBN summary data file

# first two lines of the file:
#band          mode          type          year         month           doy         posts         calls       posters
#NA            NA             A          2009            NA            NA       5007040        143724           151

# rounding function
round_n <- function(x, n) { return ( ( as.integer( (x - 1) / n) +1 ) * n ) }    # function to return next higher integral multiple of n, unless value is already such a multiple

data <- read.table(filename, header=TRUE)

# select diurnal data
diurnal_data <- subset(data, type=='D')

# drop the per-band and per-mode data
diurnal_all_bands_and_modes_data <- subset(diurnal_data, is.na(band) & is.na(mode))

# drop a bunch of columns that we don't want from the summary file
diurnal_all_bands_and_modes_data$band <- NULL
diurnal_all_bands_and_modes_data$mode <- NULL
diurnal_all_bands_and_modes_data$type <- NULL
diurnal_all_bands_and_modes_data$month <- NULL
diurnal_all_bands_and_modes_data$calls <- NULL
diurnal_all_bands_and_modes_data$posters <- NULL

# get ready to start to plot
graphics.off()

png(filename=paste(sep="", "/tmp/rbn-posts-from-summary.png"),  width=800, height=600)

x_lab <- 'DOY'

#              2009    2010   2011      2012      2013     2014    2015     2016
clrs <- c("black", "red", rgb(0.1, 0.1, 0.5), "yellow", "green", "blue", "violet", rgb(0.6, 0.2, 0.2))

# create a frame to map between year and days in the year
days_in_year <- data.frame(seq(MIN_YEAR, MAX_YEAR), 365)
names(days_in_year) <- c("year", "days")

days_in_year$days[days_in_year$year %% 4 == 0] <- 366

# set boundaries
plot(0, 0, xlim = c(0.5, 366.5), ylim = c(0, round_n(max(diurnal_all_bands_and_modes_data$posts), 1000000)), xaxt = "n", yaxt = "n", xlab = x_lab, ylab = "", type = 'n', yaxs="i")         # define the plotting region, but don't actually plot anything
rect(par("usr")[1], par("usr")[3], par("usr")[2], par("usr")[4], col = 'grey')

# now generate the plot, superimposing each year
for (this_year in seq(MIN_YEAR, MAX_YEAR))
{ this_years_data <- subset(diurnal_all_bands_and_modes_data, year==this_year)
  max_element <- days_in_year$days[this_year - MIN_YEAR + 1]
  
# set up so that this_years_data$id_365[365] = this_years_data$id_366[366] = 366, so either column can be used as a vector of abscissæ,
# depending on whether there are 365 or 366 ordinate values
  this_years_data$id_366<-seq.int(nrow(this_years_data))
  this_years_data$id_365<-((this_years_data$id_366 - 1) * 365.0 / 364.0) + 1

# remove a couple of columns that we no longer need
  this_years_data$doy <- NULL
  this_years_data$year <- NULL

# move the two new columns of days to the left of the frame: 365, then 366
  this_years_data <- (this_years_data[ c(ncol(this_years_data), ncol(this_years_data) - 1, 1:(ncol(this_years_data)-2))])


  lines(this_years_data[,(max_element-364)][1:max_element], this_years_data$posts[1:max_element], type = 'l', col = clrs[this_year - MIN_YEAR + 1], lwd = 1)  
}

title_str <- paste(sep="", 'RBN POSTS PER DAY')
title(title_str)

title(ylab = '# OF POSTS (m)', line = 2.1, cex.lab = 1.0)

x_ticks_at <- c(1, 31, 61, 91, 121, 151, 181, 211, 241, 271, 301, 331, 361)
x_labels_at <- x_ticks_at
x_tick_labels <- x_ticks_at

axis(side = 1, at = x_ticks_at, labels = FALSE )    # ticks on x axis
axis(side = 1, at = x_labels_at, labels = x_tick_labels, tick = FALSE )

y_ticks_at <- seq(0, round_n(max(diurnal_all_bands_and_modes_data$posts), 1000000), 100000)
y_labels_at <- seq(0, round_n(max(diurnal_all_bands_and_modes_data$posts), 1000000), 1000000)
y_tick_labels <- seq(0, round_n(max(diurnal_all_bands_and_modes_data$posts), 1000000) / 1000000, 1)

axis(side = 2, at = y_ticks_at, labels = FALSE )
axis(side = 2, at = y_labels_at, labels = y_tick_labels, tick = FALSE )

minx <- par("usr")[1]
maxx <- par("usr")[2]
miny <- par("usr")[3]
maxy <- par("usr")[4]

xrange <- maxx - minx
yrange <- maxy - miny

xpos <- minx + 0.025 * xrange
ypos <- miny + 0.975 * yrange

par(xpd=T, mar=c(0,0,4,0))

legend(x = xpos, y = ypos, legend = seq(MIN_YEAR, MAX_YEAR), 
       lty=c(1, 1), lwd=c(2,2), col = clrs, 
       bty = 'n', text.col = 'black')

graphics.off()


