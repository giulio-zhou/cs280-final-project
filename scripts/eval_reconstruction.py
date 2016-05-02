import numpy as np
import skimage as sk
import skimage.io as skio
from skimage.measure import compare_mse
from skimage.measure import compare_nrmse
from skimage.measure import compare_psnr
from skimage.measure import compare_ssim
import os
import sys

sse = lambda img_truth, img_rec: np.sum((img_truth - img_rec)**2)

metrics = {
    'sse': (sse, np.min),
    #'ssim': lambda x, y: 1 / compare_ssim(x, y, multichannel=True),
    'mse': (compare_mse, np.min),
    'nrmse': (compare_nrmse, np.min),
    'psnr': (compare_psnr, np.max)
}

def compute_metric(img_truth, img_rec, metric):
    r1, c1, _ = img_truth.shape
    r2, c2, _ = img_rec.shape
    metric_fn, metric_filter = metric
    result = np.empty((r1-r2+1, c1-c2+1))
    for i in range(result.shape[0]):
        for j in range(result.shape[1]):
            window = img_truth[i:i+r2, j:j+c2]
            result[i, j] = metric_fn(window, img_rec)
    return metric_filter(result)

def pixel_count(img1, img2):
    r1, c1, _ = img1.shape
    r2, c2, _ = img2.shape
    return min(r1, c1) * min(r2, c2)

def eval_directories(dir_truth, dir_rec, metric):
    files1 = sorted(os.listdir(dir_truth))
    files2 = sorted(os.listdir(dir_rec))
    i1 = 0
    i2 = 0
    total_err = 0
    total_weighted_err = 0
    total_px = 0
    while i1 < len(files1) and i2 < len(files2):
        name1 = os.path.splitext(files1[i1])[0]
        name2 = os.path.splitext(files2[i2])[0]
        if name1 == name2:
            img1 = read_img(dir_truth + '/' + files1[i1])
            img2 = read_img(dir_rec + '/' + files2[i2])
            err = compute_metric(img1, img2, metric)
            print "%s: %f" % (name1, err)
            px = pixel_count(img1, img2)
            total_err += err
            total_weighted_err += err * px
            total_px += px
            i2 += 1
        i1 += 1
    print "Average: %f" % (total_err / i2)
    print "Weighted average: %f" % (total_weighted_err / total_px)

def read_img(filename):
    img = sk.img_as_float(skio.imread(filename))
    if len(img.shape) == 2:
        img = np.dstack((img, img, img))
    return img

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        if len(sys.argv) >= 4:
            err_fn = sys.argv[3]
        else:
            err_fn = 'sse'
        eval_directories(sys.argv[1], sys.argv[2], metrics[err_fn])
