import fiftyone as fo

dataset = fo.load_dataset("open-images-v7-train-validation-test-1000")

if __name__ == "__main__":
    # Ensures that the App processes are safely launched on Windows
    session = fo.launch_app(dataset=dataset, desktop=True)
    session.wait()