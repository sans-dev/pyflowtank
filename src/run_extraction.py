import cv2
import imageio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from tools import *
from config import show_bin, save_gif, vid_slice, mouth_sizes

plt.style.use('ggplot')


def play(path, mouth_mm,vid_slice=[500,1500],show=False,save_gif=False):
    print(f"##### Setting landmarks for {path.name}...")
    is_processing = False
    is_needle = False
    inc_pos = []
    gif_list = []
    for key in pos_list.keys():
        pos_list[key] = None
    cap = cv2.VideoCapture(path.as_posix())
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    skip_counter = 0
    while (cap.isOpened()):
        # Capture frame-by-frame
        ret, img = cap.read()
        if not ret:
            # release the video capture object
            cap.release()
            # Closes all the windows currently opened.
            cv2.destroyAllWindows()
            break

        fr = img.copy()

        cv2.imshow('Frame', img)
        
        while None in list(pos_list.values()):
            for lm,pos in pos_list.items():
                if pos:
                    continue

                cv2.setMouseCallback('Frame', click_event,param=lm)
                key = cv2.waitKey(0)
                if key == 32:
                    
                    lm_img = img.copy()
                    for key,circle in pos_list.items():
                        if circle:
                            cv2.circle(lm_img, circle, 4, (0,150,255), -1)
                            cv2.putText(lm_img, key, circle, cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0,150,255), 2)
                    cv2.imshow('Frame', lm_img)
                    if not pos_list[lm]:
                        break
                elif key == ord('q'):
                    # release the video capture object
                    cap.release()
                    # Closes all the windows currently opened.
                    cv2.destroyAllWindows()
                    return
        
        mm_to_pixels = mouth_mm / point_distance(np.array(pos_list['upper_jaw']),np.array(pos_list['lower_jaw']))
            # write positions to csv
        
        lm_df = pd.DataFrame.from_dict(pos_list)
        lm_df.index = ['x','y']
        lm_df = lm_df.transpose()
        res_path = Path("results") / (path.stem + "_LM.csv")
        lm_df.to_csv(res_path)
        for key, pos in pos_list.items():
            cv2.circle(img, pos, 4, (0,150,255), -1)
            cv2.putText(img, key, pos, cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0,150,255), 2)
        cv2.imshow('Frame', img)

        ######### put algo here
        if not is_needle:
            needle = list(pos_list.values())[-1]
            is_needle = True
            start,stop = get_line_horizontal((0,img.shape[1]),needle[1])
            cv2.line(img,start,stop,color=(0,0,255),thickness=2)
            start,stop = get_line_vertical(needle[0],(0,img.shape[0]))
            cv2.line(img,start,stop,color=(0,0,255),thickness=2)
            # draw line into mouth and measure distance
            cv2.line(img,pos_list['upper_jaw'],pos_list['lower_jaw'],(255,255,0),2)
            img_const = img.copy()

        cv2.imshow('Frame', img_const)

        if not is_processing:
            key = cv2.waitKey(0)
            if key == 32:
                is_processing = True
                print(f"##### Everything set. Start processing...")    
                continue
            elif key == ord('q'):
                # release the video capture object
                cap.release()
                # Closes all the windows currently opened.
                cv2.destroyAllWindows()
                break

        # binarize region of interest
        area = 50
        _,mask = binarize_roi(fr[needle[1]-area:needle[1]+area,pos_list['upper_jaw'][0]+int(area*1.5):needle[0]],blur=(1,1))
        # make a background seperation for the whole video
        gray = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        bg = fgbg.apply(gray)
        bg[needle[1]-area:needle[1]+area,pos_list['upper_jaw'][0]+int(area*1.5):needle[0]] = mask

        if show:
            cv2.imshow('Seperation',bg)

            if cv2.waitKey(1) & 0xFF == ord('q'):
            #     # release the video capture object
                cap.release()
                # Closes all the windows currently opened.
                cv2.destroyAllWindows()
                break
        
        n_scip = 50
        # collect pixel positions and save them into numpy array
        if skip_counter > vid_slice[0] + n_scip: # skip frame for stable background seperation
            inc_pos.append(get_upper_lower_bound(bg))
            if save_gif:
                if not np.mod(skip_counter,10):
                    gif_list.append(bg)
            if skip_counter == vid_slice[1] + n_scip:
                break
        skip_counter += 1

    # release the video capture object
    cap.release()
    # Closes all the windows currently opened.
    cv2.destroyAllWindows()

    inc_pos = np.array(inc_pos)

    inc_pos[inc_pos == 0] = needle[1]
    inc_pos = fr.shape[0] - inc_pos
    inc_pos = inc_pos - (fr.shape[0] - needle[1])
    
    inc_pos = inc_pos*mm_to_pixels

    header = ['upper','lower']*inc_pos.shape[1]

    inc_mean = np.mean(inc_pos,axis=0)
    inc_pos[:,inc_mean == 0] = np.nan
    inc_pos = inc_pos.reshape(inc_pos.shape[0],inc_pos.shape[1]*inc_pos.shape[2])
    print(f"##### Saving data...")

    # create a df for comparison
    res_path = Path("results") / (path.stem + "_DATA.csv")
    df = pd.DataFrame(data=inc_pos,columns=header)
    df.to_csv(res_path.as_posix())
    res_path = Path("results") / (path.stem + "_GIF.gif")
    imageio.mimsave(res_path.as_posix(),gif_list,fps=5)
    print(f"##### Done!")
    print(f"====================================")


def main():
    video_path = Path(r'videos').glob("*.MOV")
    for vid in video_path:
        # extract id
        _id = vid.stem.split("_")[0]
        mouth_mm = mouth_sizes[_id]
        
        play(vid,mouth_mm,vid_slice=vid_slice,show=show_bin,save_gif=save_gif)

if __name__ == '__main__':
    main()