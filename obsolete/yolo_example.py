# results would be a list of Results object including all the predictions by default
# but be careful as it could occupy a lot memory when there're many images,
# especially the task is segmentation.
# 1. return as a list
results = model.predict(source="folder")

# results would be a generator which is more friendly to memory by setting stream=True
# 2. return as a generator
results = model.predict(source=0, stream=True)

for result in results:
    # Detection
    result.boxes.xyxy   # box with xyxy format, (N, 4)
    result.boxes.xywh   # box with xywh format, (N, 4)
    result.boxes.xyxyn  # box with xyxy format but normalized, (N, 4)
    result.boxes.xywhn  # box with xywh format but normalized, (N, 4)
    result.boxes.conf   # confidence score, (N, 1)
    result.boxes.cls    # cls, (N, 1)

    # Segmentation
    result.masks.data      # masks, (N, H, W)
    result.masks.xy        # x,y segments (pixels), List[segment] * N
    result.masks.xyn       # x,y segments (normalized), List[segment] * N

    # Classification
    result.probs     # cls prob, (num_class, )

# Each result is composed of torch.Tensor by default,
# in which you can easily use following functionality:
result = result.cuda()
result = result.cpu()
result = result.to("cpu")
result = result.numpy()