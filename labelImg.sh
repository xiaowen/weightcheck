# https://www.reddit.com/r/MachineLearning/comments/5o1nsi/d_recommendation_for_bounding_box_annotation/
git clone https://github.com/tzutalin/labelImg labelImg/labelImg

docker run --rm --name=labelImg -u $(id -u):$(id -g) -d -it \
-e DISPLAY=unix$DISPLAY \
-e HOME=$(pwd)/labelImg \
-w $(pwd)/labelImg \
-v $(pwd)/labelImg:$(pwd)/labelImg \
-v $(pwd)/scale/images:$(pwd)/scale/images \
-v $(pwd)/reading/images:$(pwd)/reading/images \
-v /etc/group:/etc/group:ro \
-v /etc/passwd:/etc/passwd:ro \
-v /etc/shadow:/etc/shadow:ro \
-v /etc/sudoers.d:/etc/sudoers.d:ro \
-v /tmp/.X11-unix:/tmp/.X11-unix \
tzutalin/py2qt4

docker exec -it -w $(pwd)/labelImg/labelImg labelImg make qt4py2
docker exec -it labelImg labelImg/labelImg.py
