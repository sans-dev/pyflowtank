import cv2
import imageio
import numpy as np
from pathlib import Path
from tools import *
from config import save_gif, vid_slice


def play(path,vid_slice=[500,1500],save_gif=False):
    print(f"##### Creating gif from {path.name}...")
    gif_list = []
    for key in pos_list.keys():
        pos_list[key] = None
    cap = cv2.VideoCapture(path.as_posix())
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

        n_scip = 50
        # collect pixel positions and save them into numpy array
        if skip_counter > vid_slice[0] + n_scip: # skip frame for stable background seperation
            if save_gif:
                if not np.mod(skip_counter,10):
                    gif_list.append(img)
            if skip_counter == vid_slice[1] + n_scip:
                break
        skip_counter += 1

    # release the video capture object
    cap.release()
    # Closes all the windows currently opened.
    cv2.destroyAllWindows()

    res_path = Path("results") / (path.stem + "_ORIGINAL_GIF.gif")
    imageio.mimsave(res_path.as_posix(),gif_list,fps=5)
    print(f"##### Done!")
    print(f"====================================")


def main():
    video_path = Path(r'videos').glob("*.MOV")
    for vid in video_path:
        play(vid,vid_slice=vid_slice,save_gif=save_gif)

if __name__ == '__main__':
    main()