## Requirements
* Pytorch 1.3.0 
* Torchvision 0.4.0
* Python3.7
* pretrainedmodels
* efficientnet-pytorch
* Chinese font-simhei.ttf, [Download Link](https://fontzone.net/download/simhei). Put simhei in `project_root/font`.

## How to run
### Clone Our Project
```bash
git clone https://github.com/XiangqianMa/AI-Competition-HuaWei.git
cd AI-Competition-HuaWei
```

### Prepare Dataset
Download dataset, unzip and put them into `your_data_path` directory.

Structure of the `your_data_path` folder can be like:
```bash
train_data
label_id_name.json
```

Create soft links of datasets in the following directories:

```bash 
cd AI-Competition-HuaWei
mkdir data
cd data
ln -s your_data_path huawei_data
```

### HuaWei Cloud Online Test

We use `online-service` folder to accomplish online test on HuaWei ModelArts platform.  The struct of this folder is like the following:

You should put your dependencies into `online-service/model` like this:

![image-20191121211651701](readme/image-20191121211651701.png)

If you want to import customized package in your code, import sentence should be like this:

```python
from model import xxx
```

Also, you must specified your dependencies in `config.json`:

```python
"dependencies": [
    {
        "installer": "pip",
        "packages": [
            {
                "package_name": "Pillow",
                "package_version": "5.0.0",
                "restraint": "EXACT"
            },
            {
                "package_name": "torchvision",
                "package_version": "0.2.1",
                "restraint": "EXACT"
            },
            {
                "package_name": "tqdm"
            }                
        ]
    }
]
```

## Train

```bash
cd AI-Competition-HuaWei
python train_classifier.py
```

## How to use obsutil
### Prepare obsutil
Download obsutil from [here](https://support.huaweicloud.com/utiltg-obs/obs_11_0003.html). Unzip it to `./online-service`. After unzipping,  `./online-service` folder will contain `obsutil` and `setup.sh` files

```bash
cd online-service
```

Replace the following `-i=xxxxxxx` to `-i=Access Key Id?AK?` and replace the following `-k=xxxxxxxxxxxxxxxxx` to `-k=Secret Access Key?SK?` 
```bash
./obsutil config -i=xxxxxxx -k=xxxxxxxxxxxxxxxxx -e=obs.cn-north-4.myhuaweicloud.com
```

Then, you will see feedback similar to the one below
```bash
Config file url:
  /home/zdkit/.obsutilconfig

Update config file successfully!
```

Then, execute the following code to check connectivity 
```
./obsutil ls -s
```

If the returned result contains "Bucket number is:", the configuration is correct. Just like these:
```bash
Start at 2019-11-22 15:43:11.060016056 +0000 UTC

obs://ai-competition-zdaiot
obs://test-zdaiot
Bucket number is: 2
```

### Use obsutil
Please Manually change the selected model in `online-service/model/customize_service.py` file.  And  manually change the `model` parameters in `online-service/upload.sh`.  The script will automatically find the newly modified folder from the `checkpoints/${model}` directory and copy the `model_best.pth` from it to the `online-service/model` directory.

> If you want to place the `model_best.pth` file manually, please comment out the `cp ../checkpoints/${model}/${filename}/model_best.pth online-service/model` line in the `online-service/upload.sh` file. Then manually place the weight file `model_best.pth` to the `online-service/model` directory.

Notice that, when you copy pyfiles from `models` to `online-service/model/deploy_models`, you should pay attention to these

- change import path of Python package. For example, change `from models.custom_model import CustomModel` to `from model.deploy_models.custom_model import CustomModel` in `online-service/model/deploy_models/custom_model.py`. 
- modify the parameters of `prepare_model.create_model` function in the `online-service/model/customize_service.py` and `online-service/offline_service.py` according to the actual needs.

When you first use it, you should run this:
```bash
cd online-service
./upload.sh 0
```

Then, this script will create a bucket called `ai-competition-$USER` in your OBS, create a new folder called `model_snapshots`, and upload the `./model` folder to the model_snapshots folder.

> $USER is your Linux username

If you want to update the weight file or python files. Please manually put new python files in the corresponding directory. And run this:
```bash
./upload.sh
```