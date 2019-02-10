# This doc accompanies the blog post and gives the exact commands to run to train a neural network to recognize scales.
# You'll have to modify some of this for your situation.

# Before you start, clone this repo to use the scripts referenced here
git clone https://github.com/xiaowen/weightcheck
cd weightcheck

# Then place your images and labeled data into the scale/images/ directory.
# Now we're ready to train the neural network using the following steps.

# Step 1: install the Tensorflow Object Detection API
# Follow the instructions at https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md
# The following are the condensed steps I used
git clone https://github.com/tensorflow/models.git tensorflow/models
sudo apt-get install protobuf-compiler
(cd tensorflow/models/research && protoc object_detection/protos/*.proto --python_out=.)

pip install --user tensorflow tensorboard pillow Cython
pip install --user contextlib2 lxml jupyter matplotlib pycocotools
echo $(pwd)/tensorflow/models/research > $HOME/.local/lib/python2.7/site-packages/tf-models-research.pth
echo $(pwd)/tensorflow/models/research/slim > $HOME/.local/lib/python2.7/site-packages/tf-models-research-slim.pth

# Step 2: install gcloud
# Follow the instructions at https://cloud.google.com/sdk/docs/downloads-apt-get
gcloud auth application-default login # authenticate to allow this tool to access your account

# Step 3: create a Google Cloud Platform (GCP) storage bucket
# Follow the instructions at https://cloud.google.com/storage/docs/creating-buckets
YOUR_STORAGE_BUCKET=<the name of your storage bucket> # put the name of your storage bucket into a variable for later use

# Step 4: upload a pre-trained model
curl -O http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_coco_2018_01_28.tar.gz # from https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md
tar xf ssd_mobilenet_v1_coco_2018_01_28.tar.gz --wildcards ssd_mobilenet_v1_coco_2018_01_28/model.ckpt.*
gsutil cp ssd_mobilenet_v1_coco_2018_01_28/model.ckpt.* gs://${YOUR_GCS_BUCKET}/data/

# The rest of the training instructions are for scales, so switch to the scale directory
cd scale

# Step 5: upload your custom training data; make sure your images and labels are in the images/ subdirectory
python ../labels2csv.py # converts labelImg XML files (images/*.xml) to a CSV file (annotations.csv)
python ../genrecords.py # uses the CSV file to convert your training data into *.record files
# labels.pbtxt contains the labels I used ('scale', 'reading').  If you used different ones, then update this file.
gsutil cp train.record test.record labels.pbtxt gs://${YOUR_GCS_BUCKET}/data/

# Step 6: bundle up the Tensorflow object detection source code
RESEARCH_DIR=../tensorflow/models/research # update to point to where you cloned the tensorflow models repo 
ln -s $RESEARCH_DIR/object_detection $RESEARCH_DIR/setup.py $RESEARCH_DIR/slim .
bash object_detection/dataset_tools/create_pycocotools_package.sh /tmp/pycocotools # creates /tmp/pycocotools/pycocotools-2.0.tar.gz
python setup.py sdist # creates dist/object_detection-0.1.tar.gz
(cd slim && python setup.py sdist) # creates slim/dist/slim-0.1.tar.gz

# Step 7: configure object detection (update its config file and upload it)
# pipeline.config contains configuration options for the object detection code.
# You need to input your storage bucket name.  Feel free to further modify.
sed -i "s/\${YOUR_GCS_BUCKET}/${YOUR_GCS_BUCKET}/" pipeline.config
gsutil cp pipeline.config gs://${YOUR_GCS_BUCKET}/data/

# Step 8: submit the job to ML engine to train
gcloud ml-engine jobs submit training object_detection_`date +%m_%d_%Y_%H_%M_%S` \
--module-name object_detection.model_main \
--job-dir=gs://${YOUR_GCS_BUCKET}/model \
--packages dist/object_detection-0.1.tar.gz,slim/dist/slim-0.1.tar.gz,/tmp/pycocotools/pycocotools-2.0.tar.gz \
--region us-central1 \
--runtime-version 1.9 \
--scale-tier=basic_gpu \
-- \
--model_dir=gs://${YOUR_GCS_BUCKET}/model \
--pipeline_config_path=gs://${YOUR_GCS_BUCKET}/data/pipeline.config

# Step 9: monitor the training job
PATH=$PATH:$HOME/.local/bin tensorboard --logdir=gs://${YOUR_GCS_BUCKET}/model

# Step 10: export the trained model when you're done training
CHECKPOINT_NUMBER=9938 # set this to the number in your model file name as generated during training
mkdir model
gsutil cp gs://${YOUR_GCS_BUCKET}/model/model.ckpt-${CHECKPOINT_NUMBER}.* model/
python object_detection/export_inference_graph.py \
--input_type image_tensor \
--pipeline_config_path pipeline.config \
--trained_checkpoint_prefix model/model.ckpt-${CHECKPOINT_NUMBER} \
--output_directory model/exported_graphs

# Step 11: make some inferences and check your results
python ../infer.py # use your exported model to run inference on images/*.jpg and output to detectedbboxes.csv
# You can use Jupyter (jupyter.org) to read detectedbboxes.csv and visually check your inference results
(cd .. && PATH=$PATH:$HOME/.local/bin jupyter notebook) # open ../chkinference.ipynb


# You've trained a model to recognize scales, congrats!
# A few other scripts here might come in handy:
# 1. dlphotos.py can be used to download from Google Photos (switch to the scale directory to run this).
# 2. scale2reading.py crops out the circular display from images of scales based on the inferred bounding boxes.
# 3. reading/viz.html can be used to graph your weight over time once you've trained your model to read the display.
