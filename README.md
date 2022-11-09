# pyflowtank 

<img src="logo.gif" align="center" width="300" height="200" />


This package can be used to extract inc positions whithin a flowtank. 

## Installation
First install the dependencies of pyflowtank into your virtual environment. To create a virtual environment type

```
pyhton -m venv <venvname>
```

where venvname is the name you want to give the environment,
After you've activated the environment via

```
. path/to/your/env/activate 
```
in unix and 
```
.\path\to\your\env\scripts\Activate.sh 
```
in windows, run the command

```
pip install -r requirements.txt
```

to install all dependencies into the virtual environment.


## Usage
First, create the folders **videos** and **results** in the root directory of pyflowtank.
Afterwards copy all video files you want to analyse into the **videos** folder.

In **config.py** several parameters can be configured for the inc position extraction.
For example the slice of frames which shall be analysed, as well as the landmarks of interest.
Change the **config.py** in regards of your options. 

Run the file **run_extraction.py** to start your analysis. The results will be stored in the **results** folder.
You should find several files in there.

1. _DATA.csv containts the data of the upper and lower inc boundaries in the format: ```[n_frames,frame_width*2]``` The frame_widht it multiplied by two because the upper and lower values are stored in this dimension for every pixel in an alternating manner.  

## Algorithm
pyflowtank uses image binarisation algorithms to extract the upper and lower position of the inc stream in the tank. 
In a first step several landmarks can be set.
Among these is the position of the needle which releases the inc into the tank.
The needle position, together with the upper jaw position is used to define the boundaries for a crop which is extracted from every video frame. 
This crop is treated differently from the rest of the frame, because of two issues.

1. The whole frame is binarised using a [MOG model](http://www.ai.mit.edu/projects/vsam/Publications/stauffer_cvpr98_track.pdf). It uses the change in pixel values between frame to estimate a background model which is then be used for foreground mask prediction. If the inc positions are static, the they will be included into the background model. This is often the case in laminar flow conditions when no rigid body disturbes the flow. The are from the needle to the mouth often shows this static state of inc.

2. By using a crop which closely sourounds the path of the inc in front of the mouth the backgronud becomes more homogeneous resulting in better seperation results using the [otsu thresholding method](https://ieeexplore.ieee.org/document/6313443).

The crop is insered into the frame afterwards to form a complete binarized image which is then analyzed. 
At the moment the upper and lower inc boundaries are extracted in mm relative to the height of the needle. 
