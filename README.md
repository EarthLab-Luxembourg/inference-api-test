# Inference API test

This script is a simple helper designed to show how to interract with the Inference API (for Object Detection).

## How does it work?

1. Create two folders: one to be used as input (that will contain image to be inferred) and a second one to receive the results of the inference (with boxes).
2. Launch the script adapting the command line to your specific case. Run `python3 testing.py` to get more help.
```
usage: Testing tool against Inference API [-h] --api-key The_Key
                                          --source-folder ./Images
                                          --destination-folder ./Results
                                          --api-url
                                          http://host:port/context-path
Testing tool against Inference API: error: the following arguments are required: --api-key/-k, --source-folder/-s, --destination-folder/-d, --api-url/-u
```

## Performance indication

The script displays as output the time (in seconds) spent on inference.
This is an approcimation as the evaluation also includes the calls to the API to look for the status.
Example of output:
```
This_is_Image_01.JPG	2.5551600456237793
This_is_Image_01.JPG	2.464301109313965
This_is_Image_01.JPG	2.4990789890289307
Mean 2.3333333333333
```