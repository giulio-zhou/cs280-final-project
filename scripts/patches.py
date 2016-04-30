import numpy as np
import skimage as sk
import skimage.io as skio
import sys
import os

EXTENSION = '.png'

def image_to_patches(img, patch_size, stride):
    rows, cols, ch = img.shape
    patches_x = (cols - patch_size) / stride + 1
    patches_y = (rows - patch_size) / stride + 1
    indices = np.indices((patches_y, patches_x))
    patches = np.empty((patches_y, patches_x, patch_size, patch_size, ch))

    def extract_patch(idx):
        y, x = idx
        r1, c1 = y * stride, x * stride
        r2, c2 = r1 + patch_size, c1 + patch_size
        patches[y, x, :, :, :] = img[r1:r2, c1:c2, :]
        return idx

    np.apply_along_axis(extract_patch, 0, indices)
    return patches


def image_from_patches(patches, stride):
    patches_y, patches_x, patch_h, patch_w, ch = patches.shape
    img_h = (patches_y - 1) * stride + patch_h
    img_w = (patches_x - 1) * stride + patch_w

    indices = np.indices((patches_y, patches_x))

    def stitch_row(r):
        patched_row = np.zeros((patch_h, img_w, ch))
        patched_row[:, 0:patch_w, :] = patches[r, 0]
        for c in range(1, patches_x):
            prev_idx = (c - 1) * stride + patch_w
            curr_idx = c * stride
            end_idx = curr_idx + patch_w
            if curr_idx < prev_idx:
                # Overlapping region from curr_idx to prev_dx
                overlap1 = patched_row[:, curr_idx:prev_idx, :]
                overlap2 = patches[r, c, :, 0:(prev_idx-curr_idx)]
                patched_row[:, curr_idx:prev_idx, :] = 0.5 * (overlap1 + overlap2)
                patched_row[:, prev_idx:(end_idx), :] = patches[r, c, :, (prev_idx-curr_idx):]
            else:
                patched_row[:, curr_idx:(end_idx), :] = patches[r, c]
        return patched_row

    # Reconstruct each row of patches
    stitched_rows = map(stitch_row, np.arange(patches_y))
    
    # Reconstruct rows into full image
    stitched_img = np.zeros((img_h, img_w, ch))
    stitched_img[0:patch_h, :, :] = stitched_rows[0]

    for r in range(1, patches_y):
        prev_idx = (r - 1) * stride + patch_h
        curr_idx = r * stride
        end_idx = curr_idx + patch_h
        if curr_idx < prev_idx:
            # Overlapping region from curr_idx to prev_dx
            overlap1 = stitched_img[curr_idx:prev_idx, :, :]
            overlap2 = stitched_rows[r][0:(prev_idx-curr_idx), :, :]
            stitched_img[curr_idx:prev_idx, :, :] = 0.5 * (overlap1 + overlap2)
            stitched_img[prev_idx:(end_idx), :, :] = stitched_rows[r][(prev_idx-curr_idx):, :, :]
        else:
            stitched_img[curr_idx:(end_idx), :, :] = stitched_rows[r]

    return stitched_img


def save_patches(patches, directory, num_pixels_crop=0):
    if not os.path.exists(directory):
        os.makedirs(directory)
    patches_y, patches_x, _, _, _ = patches.shape
    y_digits = len(str(patches_y))
    x_digits = len(str(patches_x))
    indices = np.indices((patches_y, patches_x))

    def save_helper(idx):
        y, x = idx
        img_file = directory + '/' + str(y).zfill(y_digits) + '_' + str(x).zfill(x_digits) + EXTENSION
        if num_pixels_crop > 0:
            skio.imsave(img_file, patches[y, x][num_pixels_crop:-num_pixels_crop,
                                                num_pixels_crop:-num_pixels_crop])
        else:
            skio.imsave(img_file, patches[y, x])
        return idx

    np.apply_along_axis(save_helper, 0, indices)


def load_patches(directory):
    files = os.listdir(directory)
    patches_y, patches_x = os.path.splitext(files[-1])[0].split('_')
    patches_y = int(patches_y)
    patches_x = int(patches_x)
    y_digits = len(str(patches_y))
    x_digits = len(str(patches_x))
    indices = np.indices((patches_y, patches_x))

    patch0 = skio.imread(directory + '/' + files[0])
    rows, cols, ch = patch0.shape
    patches = np.empty((patches_y, patches_x, rows, cols, ch))

    def load_helper(idx):
        y, x = idx
        img_file = directory + '/' + str(y).zfill(y_digits) + '_' + str(x).zfill(x_digits) + EXTENSION
        img = sk.img_as_float(skio.imread(img_file))
        patches[y, x, :, :, :] = img
        return idx 

    np.apply_along_axis(load_helper, 0, indices)
    return patches


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        img_file = sys.argv[1]
        EXTENSION = os.path.splitext(img_file)[-1]
        # Split file path and remove the extension
        prefix = img_file.split('/')[-1][:-4]
        save_dir = sys.argv[2] + '/' + prefix
        print save_dir
        img = sk.img_as_float(skio.imread(img_file))
        # Make sure black and white images have a third dimension
        if len(img.shape) == 2:
            img = np.dstack((img, img, img))
        patches = image_to_patches(img, 33, 14)
        pixels_to_crop = 0
        if len(sys.argv) > 3:
            pixels_to_crop = int(sys.argv[3])
        save_patches(patches, save_dir, num_pixels_crop=pixels_to_crop)
