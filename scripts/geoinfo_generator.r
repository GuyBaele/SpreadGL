list.of.packages <- c("treeio", "tidytree", "sp", "getopt")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
library(treeio)
library(getopt)

spec <- matrix(
  c("type", "t", 8, "character", "Type of space in phylogeography",
    "annotation", "a", 8, "character", "Annotation that stores location data",
    "input", "i", 8, "character",  "Input filename",
    "output", "o", 8, "character",  "Output filename"),
  byrow = TRUE, ncol = 5)
opt <- getopt(spec=spec)

if( is.null(opt$type) || is.null(opt$annotation) || is.null(opt$input) || is.null(opt$output)){
    cat(paste(getopt(spec=spec, usage = T)))
    cat("Please provide all of the above arguments.", "\n")
    quit()
}

setwd('..')
file <- treeio::read.beast(opt$input)
if(opt$type == "discrete"){
  df <- data.frame(location = file@data[[opt$annotation]])
  }
if(opt$type == "continuous"){
  df <- as.data.frame(do.call(rbind, file@data[[opt$annotation]]))
  }
write.csv(df, opt$output, row.names=FALSE)
print("Completed!")