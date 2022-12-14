# YOLOv3 🚀 by Ultralytics, GPL-3.0 license
"""
Run inference on images, videos, directories, streams, etc.

Usage:

python auto_label.py --weights weights/yolov3-spp.pt 
python auto_label.py --weights weights/yolov3-spp.pt --classes 0 --source invasion/train/images/

"""

import argparse
import os
import sys
from pathlib import Path

import time
import cv2
import torch
import torch.backends.cudnn as cudnn

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync
from utils.augmentations import letterbox

import numpy as np

def img_preprocessing(img, img_size=640, stride=32):

    # img0 = cv2.flip(img, 1)  # flip left-right
    img0 = img
    img0 = letterbox(img0, img_size, stride=stride)[0]
    img0 = img0.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    img0 = np.ascontiguousarray(img0)

    return img0

def auto_label(im, xyxy, cls):
    x0, y0, x1, y1 = float(xyxy[0].cpu()), float(xyxy[1].cpu()), float(xyxy[2].cpu()), float(xyxy[3].cpu())

    total_x , total_y = im.shape[1], im.shape[0]

    print(im.shape)
    
    print(x0, y0, x1, y1)
    
    nx0, nx1 = x0 / total_x, x1 / total_x
    ny0, ny1 = y0 / total_y, y1 / total_y


    nw = nx1 - nx0
    nh = ny1 - ny0

    ncx = nx0 + nw/2
    ncy = ny0 + nh/2



    label_txt = str(int(cls.cpu()))+' '+ str(ncx) + ' '+ str(ncy) +' '+ str(nw) +' '+ str(nh) +'\n'
    print(label_txt)

    return label_txt


@torch.no_grad()
def run(weights=ROOT / 'yolov3.pt',  # model.pt path(s)
        source=ROOT / 'data/images',  # file/dir/URL/glob, 0 for webcam
        imgsz=640,  # inference size (pixels)
        conf_thres=0.80,  # confidence threshold
        iou_thres=0.80,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='0',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img=False,  # show results
        save_txt=False,  # save results to *.txt
        save_conf=False,  # save confidences in --save-txt labels
        save_crop=False,  # save cropped prediction boxes
        nosave=False,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        update=False,  # update all models
        project=ROOT / 'runs/detect',  # save results to project/name
        name='exp',  # save results to project/name
        exist_ok=False,  # existing project/name ok, do not increment
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
        ):

    source = str(source)

    # Load model
    device = select_device(device)
    
    model = DetectMultiBackend(weights, device=device, dnn=dnn)
    stride, names, pt, jit, onnx = model.stride, model.names, model.pt, model.jit, model.onnx
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    # Half
    half &= pt and device.type != 'cpu'  # half precision only supported by PyTorch on CUDA
    if pt:
        model.model.half() if half else model.model.float()

    # Dataloader
    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt and not jit)
    bs = 1  # batch_size
    vid_path, vid_writer = [None] * bs, [None] * bs

    # Run inference
    if pt and device.type != 'cpu':
        model(torch.zeros(1, 3, *imgsz).to(device).type_as(next(model.model.parameters())))  # warmup
    dt, seen = [0.0, 0.0, 0.0], 0
    # for path, im, im0s, vid_cap, s in dataset:
    
    # video_name = "videos/fallen_test_2.mp4"
    # video_name = "videos/0.jpg"
    data_path = source

    # cap_main = cv2.VideoCapture(video_name)
    
    for img_name in os.listdir(data_path):

        txt_file_name = img_name[:-3] + "txt"
        print(txt_file_name)

        t0 = time.time()
        cap_main = cv2.VideoCapture(data_path + img_name)
        ret, frame = cap_main.read()

        im = img_preprocessing(frame)

        im = torch.from_numpy(im).to(device)
        im = im.half() if half else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim

        # # Inference
        # # visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False

        torch.cuda.synchronize()
        pred = model(im, augment=augment, visualize=False)

        # # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        torch.cuda.synchronize()
        print(pred)

        # Second-stage classifier (optional)
        # pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)

        # # Process predictions

        total_label_txt = ''

        for i, det in enumerate(pred):  # per image
            seen += 1
            im0 =  frame.copy()
            # s += f'{i}: '

            annotator = Annotator(im0, line_width=line_thickness, example=str(names))
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    # s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                
                # Write results
                for *xyxy, conf, cls in reversed(det):
                    c = int(cls)  # integer class

                    # label = names[c] #None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                    label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                    annotator.box_label(xyxy, label, color=colors(c, True))

                    label_txt = auto_label(frame, xyxy, cls)

                    total_label_txt += label_txt

        #     # Stream results
            im0 = annotator.result()
            print(1 / (time.time() - t0))

        with open('auto_label_data/' + txt_file_name, 'w') as newfile:
            newfile.write(total_label_txt)

        if True:
            cv2.imshow("main_frame", im0)
            key = cv2.waitKey(1)

            if key == 27: break

    cv2.destroyAllWindows()
    # pipeline.stop()

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default=ROOT / 'yolov3.pt', help='model path(s)')
    parser.add_argument('--source', type=str, default=ROOT / 'data/images', help='file/dir/URL/glob, 0 for webcam')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float, default=0.50, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
    parser.add_argument('--device', default='0', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='show results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default=ROOT / 'runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    print_args(FILE.stem, opt)
    return opt


def main(opt):
    # check_requirements(exclude=('tensorboard', 'thop'))
    run(**vars(opt))


if __name__ == "__main__":
    opt = parse_opt()
    main(opt)
