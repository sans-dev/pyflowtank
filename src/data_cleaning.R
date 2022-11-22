library(readr)
library(tidyr)
library(dplyr)

# path to the folder where the results are 
results_path <- "X:\\pyflowtank\\results"

files <- list.files(results_path,pattern = "*.csv")

# loop over files and read in data and landmarks
for (f in files){
  print("next is...")
  print(f)
  
  # split up filename for naming columns and checking whether its a csv containing upper/lower data or landmarks 
  sub_str <- unlist(strsplit(f,split= "_"))
  if (tail(sub_str,n=1) == "DATA.csv"){
    dat <- read_csv(file.path(results_path,f))
    
    # clean up the dataframe. Delete columns not needed, rename and add frame column
    dat$...1 <- NULL
    colnames(dat)[grepl("upper",colnames(dat))] <- "upper"
    colnames(dat)[grepl("lower",colnames(dat))] <- "lower"
    dat <- cbind(frame = 1:nrow(dat),dat)
    
    #convert to long format and add columns from filename
    dat_long <- pivot_longer(dat,cols=names(dat)[names(dat) == "upper" | names(dat) == "lower"],names_to="position")
    dat_long$species <- sub_str[1]
    dat_long$disect <- sub_str[2]
    dat_long$iter <- sub_str[3]
    dat_long$needle_pos <- sub_str[4]
    
    # read in landmarks and make some reshaping
    lm_str <- str_replace(f, "DATA", "LM")
    landmarks <- read_csv(file.path(results_path,lm_str)) 
    lm_long <- pivot_longer(landmarks,cols =names(landmarks)[names(landmarks) == "x" | names(landmarks) == "y"],names_to = "coords")
    lm_wide <- spread(lm_long, key = ...1,value = value)
    
    # merge landmarks into data
    dat_long$operculum <- data.frame(t(lm_wide$operculum))
    dat_long$GA1 <- data.frame(t(lm_wide$GA1))
    dat_long$upper_jaw <- data.frame(t(lm_wide$upper_jaw))
    dat_long$lower_jaw <- data.frame(t(lm_wide$lower_jaw))
    dat_long$needle <- data.frame(t(lm_wide$needle))
    
    #append video csvs 
    if (exists('dat_all') && is.data.frame(get('dat_all'))){
      dat_all <- bind_rows(dat_all,dat_long)
    }else{
      dat_all <- dat_long
    }
  }
}

print("done...")