show_bin = False # flag that defines if the binarized video is presented or not
vid_slice = [500,1500] # video slice of frames used for analysis
save_gif = True # flag which controls whether a gif is extracted from the video

# defines the mouth size in mm
# The key is an unique identifier for the fish in the video and shoud match to a substring in the video file
mouth_sizes = {
    'CH' : 13,
    'RK' : 30,
    'SS1' : 20,
    'EE' : 19,
    'SP' : 26,
}

# List of anatomical positions. Expect of needle the names can be changed by the user
pos_list = {
    'operculum' : None,
    'GA1': None,
    'upper_jaw' : None,
    'lower_jaw' : None,
    'needle' : None
}