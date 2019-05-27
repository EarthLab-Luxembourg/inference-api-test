"""
Utility to check the inference performances

This code is not optimized for the performance but the measurement of the inference time.
Especially, there is no parallelisation using the Message Queuing.
The images are submitted sequentially and the submission of the next image is only performed
when the previous image is finished.

How to use it?
1. Place the images, as jpg, in the subfolder `Images/`
2. Run `python3 testing.py`
3. The result of the inference will be placed in the folder `Results`

Output provides the different time measurements.

"""
import os
from typing import Tuple
import time
import base64
import json
import urllib.parse
from argparse import ArgumentParser
import requests


def save(base64_image: str, filename: str):
    """Function to save a base64 image in the specified folder

    :param base64_image: Inferred image (with boxes) as base64
    :type base64_image: string
    :param filename: complete path pointing to the file to save
    :type filename: string
    """
    imgdata = base64.b64decode(base64_image)
    with open(filename, "wb") as image_file:
        image_file.write(imgdata)


def monitor_inference(inference_id: str, start_clock: float) -> Tuple(str, float):
    """Function to monitor an inference: waiting for the inference to be performed
    The code sends requests with field filtering (X-Fields) and, when the inference is finished,
    it sends a full requests to return the inferred_image_with_box.

    :param inference_id: Inference ID
    :type inference_id: str
    :param float: Starting time
    :type float: float
    :return: Tuple containing the inferred image (with the boxes) and the processing time
    :rtype: Tuple
    """

    url = API_GET_URL.format(urllib.parse.quote_plus(inference_id))
    req_get = requests.get(url=url, headers={"Api-Key": API_KEY, "X-Fields": "status"})
    response = req_get.json()
    while response["status"]["state"] == "NEW":
        req_get = requests.get(
            url=url, headers={"Api-Key": API_KEY, "X-Fields": "status"}
        )
        response = req_get.json()
        if response["status"]["state"] == "DONE":
            diff = time.time() - start_clock
            req_get = requests.get(url=url, headers={"Api-Key": API_KEY})
            data = req_get.json()
            return data["inferred_image_with_box"], diff


def main():
    """Main function to list, read and submit images recording the time spent
    """
    images = os.listdir(path=IMAGE_PATH)
    time_inference = []
    for image_name in images:
        with open(os.path.join(IMAGE_PATH, image_name), "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            payload = {"image": encoded_string.decode(), "metadata": {}}

            req_post = requests.post(
                url=API_POST_URL,
                data=json.dumps(payload),
                headers={
                    "Api-Key": API_KEY,
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            start_clock = time.time()
            if req_post.status_code == 201:
                response = req_post.json()
                inferred_image_with_box, diff = monitor_inference(
                    inference_id=response["id"], start_clock=start_clock
                )  # Blocking call
                save(inferred_image_with_box, os.path.join(OUTPUT_PATH + image_name))
                time_inference.append(diff)
                print("{}\t{}".format(image_name, diff))
            else:
                print("{}\tError {}".format(image_name, req_post.status_code))
    print("Mean\t\t {}".format(sum(time_inference) / float(len(time_inference))))


if __name__ == "__main__":
    PARSER = ArgumentParser(prog="Testing tool against Inference API")
    PARSER.add_argument(
        "--api-key",
        "-k",
        required=True,
        help="API Key to use when accessing the API",
        metavar="The_Key",
        type=str,
    )
    PARSER.add_argument(
        "--source-folder",
        "-s",
        required=True,
        help="The folder in which the sources images are located",
        metavar="./Images",
        type=str,
    )
    PARSER.add_argument(
        "--destination-folder",
        "-d",
        required=True,
        help="The folder in which the infered images should be saved",
        metavar="./Results",
        type=str,
    )
    PARSER.add_argument(
        "--api-url",
        "-u",
        required=True,
        help="Base URL of the inference API",
        metavar="http://host:port/context-path",
        type=str,
    )
    ARGS = PARSER.parse_args()
    IMAGE_PATH = ARGS.source_folder
    OUTPUT_PATH = ARGS.destination_folder
    API_KEY = ARGS.api_key
    API_BASE_URL = ARGS.api_url
    assert os.path.isdir(IMAGE_PATH), "Sorry, the folder {} should exists".format(
        IMAGE_PATH
    )
    assert os.path.isdir(OUTPUT_PATH), "Sorry, the folder {} should exists".format(
        OUTPUT_PATH
    )
    API_POST_URL = os.path.join(API_BASE_URL, "internal/image-detection-inferences/")
    API_GET_URL = os.path.join(API_BASE_URL, "internal/image-detection-inferences/{}")
    main()
