import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from MultiPlanarUNet.logging import ScreenLogger


def save_images(train, val, out_dir, logger):
    logger = logger or ScreenLogger()
    # Write a few images to disk
    im_path = out_dir
    if not os.path.exists(im_path):
        os.mkdir(im_path)

    training = train[0]
    if val is not None and len(val) != 0:
        validation = val[0]
        v_len = len(validation[0])
    else:
        validation = None
        v_len = 0

    logger("Saving %i sample images in '<project_dir>/images' folder"
           % ((len(training[0]) + v_len) * 2))
    for rr in range(2):
        for k, temp in enumerate((training, validation)):
            if temp is None:
                # No validation data
                continue
            X, Y, W = temp
            for i, (xx, yy, ww) in enumerate(zip(X, Y, W)):
                # Make figure
                fig = plt.figure(figsize=(10, 4))
                ax1 = fig.add_subplot(121)
                ax2 = fig.add_subplot(122)

                # Plot image and overlayed labels
                chnl, view, _ = imshow_with_label_overlay(ax1, xx, yy)

                # Plot histogram
                ax2.hist(xx.flatten(), bins=200)

                # Set labels
                ax1.set_title("Channel %i - Axis %i - "
                              "Weight %.3f" % (chnl, view, ww), size=18)

                # Get path
                out_path = im_path + "/%s%i.png" % ("train" if k == 0 else
                                                    "val", len(X) * rr + i)

                with np.testing.suppress_warnings() as sup:
                    sup.filter(UserWarning)
                    fig.savefig(out_path)
                plt.close(fig)


def imshow(ax, image, channel=None, axis=None, slice=None, cmap="gray"):
    """
    Imshow an image of dim 2 or dim 3

    Args:
        ax:
        image:
        channel:
        axis:
        slice:
        cmap:

    Returns:

    """
    # Get channel to plot
    if channel is None:
        channel = np.random.randint(0, image.shape[-1], 1)[0]

    # Get image channel
    image = image[..., channel]
    img_dims = image.ndim

    if img_dims == 3 and axis is None:
        shape = np.array(image.shape[:-1])
        if np.all(shape == shape[0]):
            axis = np.random.randint(0, shape.ndim, 1)[0]
        else:
            axis = np.argmin(shape)
    elif axis is None:
        axis = 0

    # Move the chosen axis forward
    image = np.moveaxis(image, axis, 0)

    if img_dims == 3:
        if slice is None:
            # Get a random slice around the middle of the axis
            slice = np.random.randint(0 + (len(image) // 3),
                                      len(image) - (len(image) // 3), 1)[0]
        im_slice = image[slice]
    else:
        im_slice = image

    # Imshow
    ax.imshow(im_slice, cmap=cmap)

    return channel, axis, slice


def imshow_with_label_overlay(ax, image, label, channel=None, axis=None,
                              slice=None, im_cmap="gray", lab_cmap=None,
                              lab_alpha=0.7):
    """
    Imshow an image of dim 2 or dim 3 with labels overlayed on a single ax

    Args:
        ax:
        image:
        label:
        channel:
        axis:
        im_cmap:
        lab_cmap:
        lab_alpha:

    Returns:

    """
    from MultiPlanarUNet.utils import pred_to_class

    # Plot the image
    channel, axis, slice = imshow(ax, image, channel, axis, slice, im_cmap)

    # Get int labels if needed, otherwise returns identity
    img_dims = image.ndim-1
    label = pred_to_class(label, img_dims=img_dims, has_batch_dim=False)

    # Move the chosen axis forward
    label = np.moveaxis(label, axis, 0)

    if img_dims == 3:
        lab_slice = label[slice]
    else:
        lab_slice = label

    # Overlay masked label image
    masked_lab = np.ma.masked_where(lab_slice == 0, lab_slice)

    # Imshow labels
    ax.imshow(masked_lab, alpha=lab_alpha, cmap=lab_cmap)

    return channel, axis, slice


def imshow_orientation(*args, show=False, cmap="gray"):

    fig = plt.figure()
    ind = 1
    for i in range(3):
        for j, im in enumerate(args):
            ax = fig.add_subplot(3, len(args), ind)
            im_ind = np.random.randint(0, im.shape[i], 1)[0]
            if i == 0:
                im_slice = im[im_ind]
            elif i == 2:
                im_slice = im[:, im_ind]
            else:
                im_slice = im[..., im_ind]

            ax.imshow(im_slice, cmap=cmap)
            ax.set_title("Image %i" % j)
            ax.axis("off")
            ind += 1

    fig.tight_layout()
    if show:
        plt.show()
    else:
        return fig


def plot_all_training_curves(glob_path, out_path, raise_error=False, **kwargs):
    try:
        from glob import glob
        paths = glob(glob_path)
        if not paths:
            raise OSError("File pattern {} gave none or too many matches " \
                          "({})".format(glob_path, paths))
        out_folder = os.path.split(out_path)[0]
        for p in paths:
            if len(paths) > 1:
                # Set unique names
                uniq = os.path.splitext(os.path.split(p)[-1])[0]
                f_name = uniq + "_" + os.path.split(out_path)[-1]
                save_path = os.path.join(out_folder, f_name)
            else:
                save_path = out_path
            plot_training_curves(p, save_path, **kwargs)
    except Exception as e:
        s = "Could not plot training curves."
        if raise_error:
            raise RuntimeError(s) from e
        print(s)


def plot_training_curves(csv_path, save_path, logy=False):
    # Read CSV file
    df = pd.read_csv(csv_path)

    # Prepare plot
    fig = plt.figure(figsize=(12, 12))
    ax1 = fig.add_subplot(311)

    # Get epoch, training and validation loss vectors
    epochs = df["epoch"] + 1
    train_loss = df["loss"]
    val_loss = df.get("val_loss")

    if logy:
        train_loss = np.log10(train_loss)
        if val_loss is not None:
            val_loss = np.log10(val_loss)

    # Plot
    ax1.plot(epochs, train_loss, lw=3, color="darkblue", label="Training loss")
    if val_loss is not None:
        ax1.plot(epochs, val_loss, lw=3, color="darkred", label="Validation loss")

    # Add legend, labels and title
    leg = ax1.legend(loc=0)
    leg.get_frame().set_linewidth(0)
    ax1.set_xlabel("Epoch", size=16)
    ax1.set_ylabel("Loss" if not logy else "$\log_{10}$(Loss)", size=16)
    ax1.set_title("Training %sloss" % ("and validation " if val_loss is not None else ""), size=20)

    # Make second plot
    ax2 = fig.add_subplot(312)

    # Get all other columns
    no_plot = ("lr", "learning_rate", "epoch", "loss", "val_loss",
               "train_time_total", "train_time_epoch")
    to_plot = [col for col in df.columns if col not in no_plot]

    for col in to_plot:
        ax2.plot(epochs, df[col], label=col, lw=2)

    # Add legend, labels and title
    leg = ax2.legend(loc=0)
    leg.get_frame().set_linewidth(0)
    ax2.set_xlabel("Epoch", size=16)
    ax2.set_ylabel("Metric", size=16)
    ax2.set_title("Training and validation metrics", size=20)

    # Plot learning rate
    lr = df.get("lr")
    if lr is None:
        lr = df.get("learning_rate")
    if lr is not None:
        ax3 = fig.add_subplot(313)
        ax3.step(epochs, lr)
        ax3.set_xlabel("Epoch", size=16)
        ax3.set_ylabel("Learning Rate", size=16)
        ax3.set_title("Learning Rate", size=20)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig.number)


def plot_views(views, out_path):
    from mpl_toolkits.mplot3d import Axes3D

    # Create figure, 3D
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")

    # Set axes
    ax.set_xlim(-0.6, 0.6)
    ax.set_ylim(-0.6, 0.6)
    ax.set_zlim(-0.6, 0.6)

    # Plot unit sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)

    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    z_f = np.zeros_like(y)

    ax.plot_surface(x, y, z, alpha=0.1, color="darkgray")
    ax.plot_surface(x, y, z_f, alpha=0.1, color="black")

    # Plot basis axes
    ax.plot([-1, 1], [0, 0], [0, 0], color="blue", linewidth=0.7)
    ax.plot([0, 0], [-1, 1], [0, 0], color="red", linewidth=0.7)
    ax.plot([0, 0], [0, 0], [-1, 1], color="green", linewidth=0.7)

    # Plot views
    for v in views:
        c = np.random.rand(3,)
        ax.scatter(*v, s=50, color=c)
        ax.scatter(*v, s=50, color=c)
        ax.plot([0, v[0]], [0, v[1]], [0, v[2]], color=c, linewidth=2)

        # Plot dashed line to XY plane
        ax.plot([v[0], v[0]], [v[1], v[1]], [0, v[2]], color="gray",
                linewidth=1, linestyle="--")

    ax.view_init(30, -45)
    ax.grid(False)
    ax.axis("off")
    fig.savefig(out_path)
