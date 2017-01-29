#!/usr/bin/Rscript

# generate comparison plot of several stations' signals against that of a single station

# compare-multiple-sigs.R start-date end-date band continent call-1 call-2 ... call-n
# e.g.,
# compare-multiple-sigs[.R] 20111126 20111126 10m EU N7DR K0ALT N2IC K0RF

  MIN_DATA_POINTS <- 10  							# minimum number of data points before we have enough data for an analysis of the mean
  colour_scale  <- colorRampPalette(c('blue', 'green', 'yellow', 'red'))  	# colour scale with standard colour shape
  BAR_WIDTH <- 0.25								# width of bar, in units in which 1 = (1 / n-calls) of the width of the plot
  bg_colour <- colours()[342]							# colour for background of plot
  font_family <- 'Droid Sans Mono'  						# monospaced font
  
# -- Nothing below this line should need to be changed  
  
# read arguments from command line
  args <- commandArgs(TRUE)
  
  start <- args[1]
  end <- args[2] 
  band <- args[3]
  continent <- args[4]
  call1 <- args[5]					# master call
  call <- tail(args, length(args) - 5)			# comparison calls
  
# create versions of the calls with / replaced by -
  safe_call1 <- gsub("/", "-", call1)
  safe_call <- gsub("/", "-", call)
  
# turn off default graphics device
  graphics.off()
  
  filename <- paste(sep="", safe_call1, "-", safe_call, "-", band, "-", continent, "-", start, "-", end, ".data")	# files from which data are to be read
 
  data <- list()
 
  for(num in 1:length(filename))
  { data[[num]] <- read.table(filename[num])		# read data for each comparison call
  }

 # get global minimum and maximum
  y_min <- min(unlist(data))
  y_max <- max(unlist(data))

# function to return next higher integral multiple of <y>, unless value <x> is already such a multiple
  round_n <- function(x, y) 
  { val <- ( ( as.integer( (x - 1) / y) + 1 ) * y ) 
  
    if (val == x) return (val)
    
    if (x < 0) return (val - y)
    
    return (val)
  }
 
# min and max number of dB, rounded to nearest 5dB
  y_min <- round_n(y_min, 5)  
  y_max <- round_n(y_max, 5)
  
#  y_range <- y_max - y_min	# dB
  n_bins <- y_max - y_min + 1
  
# open the graphics device
  png(filename=paste(sep="", safe_call1, "-", band, "-", continent, "-", start, "-", end, ".png"), width=800, height=600)

# define two screens: one for the plot, one for the legend
  screen_1 <- c(0.0, 0.9, 0.0, 1.0)
  screen_2 <- c(0.9, 1.0, 0.0, 1.0)
  
  screen_numbers <- split.screen(matrix( c(screen_1, screen_2), byrow = T, ncol = 4))  # we don't actually use the return value, but the assignment stops it from being printed

# the main plot
  screen(1)
  
  plot(0, 0, type = 'n', xlim = c(0, 1), ylim = c(y_min - 0.5, y_max + 0.5), xaxt = "n", yaxt = "n", xlab = '', ylab = '', main = '')  # define the plotting region, but don't actually plot anything
  rect(par("usr")[1], par("usr")[3], par("usr")[2], par("usr")[4], col = bg_colour)      # set the background colour

# place the y axis label at the top
  loc <- par("usr")
  text(loc[1] - 0.01, loc[4], "dB", xpd = T, adj = c(1,0))
  
# x axis labels
  x_labels <- call
  x_labels_at <- seq(0, 1, 1 / length(call))  
  x_labels_at <- head(x_labels_at, length(call))
  x_labels_at <- x_labels_at + ( 1 / (2 * length(call)) )
  
  axis(side = 1, at = x_labels_at, labels = x_labels, family = font_family, las = 1, lwd = 0)
  
# slash the zeroes in the calls
  slashes <- gsub("[A-Z1-9/]", " ", x_labels)
  slashes <- gsub("0", "/", slashes)

  axis(side = 1, at = x_labels_at, labels = slashes, family = font_family, las = 1, lwd = 0)
 
  par(new=TRUE)
  
# title; the call might need a slashed zero
  title_str <- paste(sep="", call1, " ", band, " ", continent, " ", start, " to ", end)  
  title(title_str, family = font_family)
  
  slashes <- gsub("[A-Z1-9/]", " ", ignore.case = T, call1)
  slashes <- gsub("0", "/", slashes)

  title_str_2 <- paste(sep="", " ", band, " ", continent, " ", start, " to ", end)
  slashes_2 <- gsub(".", " ", title_str_2) 
  title_str <- paste(sep="", slashes, slashes_2)
  title(title_str, family = font_family)

# y axis
   y_ticks_at <- seq(y_min, y_max, 5)
   axis(side = 2, at = y_ticks_at, las = 1, lwd = 1 )
  
# what is the highest number in the histograms?
  freq_max <- 0
  
  for (nc in 1:length(call))
  { dt <- data[[nc]]
    tab <- table(dt)
    df <- as.data.frame(tab)
    freq_max <- max(freq_max, df$Freq)
  }
  
# round upwards to multiple of 5
  freq_max <- round_n(freq_max, 5)
  
  cs <- colour_scale(freq_max)  # normalise the colour scale
  
# plot the data
  for (nc in 1:length(call))
  { dt <- data[[nc]]
    names(dt) <- "dB"
 
# because we don't know the actual variance of the difference distribution, we use the t distribution  
    sample_size <- length(dt$dB)
    dof <- sample_size - 1
    factor <- qt(c(0.995), dof)    # 99% two-tailed quantile
   
# calculate statistical metrics, assuming that the CLT is applicable
    mu <- mean(dt$dB)
    stdev <- sd(dt$dB)
    se <- stdev / sqrt(sample_size)    # standard error of the mean
 
    dual_factor <- outer(factor, c(-1, 1), FUN="*")  # both tails
    bounds <- mu + (dual_factor * se)                # 99% confidence limits when the underlying variance is not known
 
    tab <- table(dt)			# convert to table
    
    par(new=TRUE)
  
# left and right of this vertical band
    xleft <- ( (nc - 1) / length(call) )
    xright <- xleft + 1 / length(call)
    xwidth <- xright - xleft
    
    for (nb in 1:n_bins)
    { freq <- tab[names(tab) == (y_min + nb - 1)]
    
      { par(new = TRUE)
      
# colour according to gradient, or make dark grey if no measurements
        if (length(freq) == 0)
        { colour <- "#404040"
          freq <- 0
        }
        else
        { colour <- cs[freq]
        }
      
# the central bar
        bar_width <- BAR_WIDTH * xwidth
      
        left <- xleft + (xwidth - bar_width) / 2
        right <- xright - (xwidth - bar_width) / 2
       
        bottom <- y_min - 0.5 + ( nb - 1 )
        top <- bottom + 1
 
        rect(left, bottom, right, top, col = colour, border = 'black', lwd = 1)            # plot it
    
# the histogram    
        right <- left - bar_width / 2
        left <- left - ( freq / freq_max ) * bar_width - bar_width / 2
  
        rect(left, bottom, right, top, col = colour, border = NA)            # plot it     
      }    
    }
    
# the 99% confidence interval 
    colours <- col2rgb('blue4')
    colours <- colours / 255
    colour <- rgb(colours[1], colours[2], colours[3], alpha = 0.5)
        
    if (length(dt$dB) >= MIN_DATA_POINTS) 
    { rect(xleft, bounds[1, 1], xright, bounds[1, 2], col = colour)  # plot 95% and 99% confidence bars
    }
  }
  
# display the gradient  
  screen(2)
  
  par(mar = rep(0, 4))    # so we can use the entire area
  plot(c(0,2), c(0, 1), type = 'n', axes = F, xlab = '', ylab = '', main = '')  # define the plotting region, but don't actually plot anything
 
  y_labels <- seq(0 , freq_max, l = ((freq_max / 5) + 1))
  y_labels[1] <- 1
  
  y_labels_at <- ( (y_labels - 1) * (0.9 - 0.1) / (freq_max - 1) ) + 0.1
  
  text(x=1.5, y = y_labels_at, labels = y_labels )  # legend 
  text(x= 0.5, y = 0.925, labels = c('Counts'))                                                                                    # title
 
  legend_image <- as.raster(matrix(colour_scale(y_max - y_min), ncol = 1))
  rasterImage(legend_image, 0.9, 0.9, 0.1, 0.1, angle = 0)                     # parameters cause the gradient to appear in the correct direction

# legend for the confidence interval
  colours <- col2rgb('blue4')
  colours <- colours / 255
  colour <- rgb(colours[1], colours[2], colours[3], alpha = 0.5)
  
  rect(0, 0.05, 0.5, 0.09, col = colour, border = NA)            # plot it
  text(0.90, 0.08, "99%")
  text(0.90, 0.06, "conf.")

# logo
  text(x = 0.7, y = 0.025, labels = c('N7DR'))                                                                                    # title
  rect(xl = 0.20, yb = 0.01, xr = 1.20, yt = 0.04, col = NA, lwd = 2)
  
# we're done; close the device and exit
  graphics.off()
