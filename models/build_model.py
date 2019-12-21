import torch
import torch.optim as optim
from torch.optim import lr_scheduler
from models.custom_model import CustomModel
from models.custom_attention_model import CustomLocalAttentionModel


class PrepareModel:
    """准备模型和优化器
    """

    def __init__(self):
        pass

    def create_model(self, model_type, classes_num, drop_rate=0, pretrained=True):
        """创建模型
        Args:
            model_type: str, 模型类型
            classes_num: int, 类别数目
            drop_rate: float, 分类层中的drop out系数
            pretrained: bool, 是否使用预训练模型
        """
        print('Creating model: {}'.format(model_type))
        model = CustomModel(model_type, classes_num, drop_rate=drop_rate, pretrained=pretrained)
        return model

    def create_local_attention_model(self, model_type, classes_num, last_stride=2, drop_rate=0,
                                     pretrained=True, use_local_attention=True):
        """创建模型
        Args:
            model_type: str, 模型类型
            classes_num: int, 类别数目
            last_stride: int, resnet最后一个下采样层的步长
            drop_rate: float, drop rate
            pretrained: bool, 是否使用预训练模型
            use_local_attention: bool, 是否使用局部attention机制
        """
        print('Creating model: {}'.format(model_type))
        model = CustomLocalAttentionModel(model_type, classes_num, last_stride, drop_rate, pretrained, use_local_attention)
        return model

    def create_optimizer(self, model_type, model, config):
        """返回优化器

        Args:
            model_type: 模型类型
            model: 待优化的模型
            config: 配置
        Return:
            optimizer: 优化器
        """
        ignored_params = list(map(id, model.module.classifier.parameters()))
        base_params = filter(lambda p: id(p) not in ignored_params and p.requires_grad, model.module.parameters())
        print('Creating optimizer: %s' % config.optimizer)
        if config.optimizer == 'Adam':
            optimizer = optim.Adam(
                [
                    {'params': base_params, 'lr': 0.1 * config.lr},
                    {'params': model.module.classifier.parameters(), 'lr': config.lr}
                ], weight_decay=config.weight_decay)
        elif config.optimizer == 'SGD':
            optimizer = optim.SGD(
                [
                    {'params': base_params, 'lr': 0.1 * config.lr},
                    {'params': model.module.classifier.parameters(), 'lr': config.lr}
                ], weight_decay=config.weight_decay, momentum=0.9)

        return optimizer

    def create_lr_scheduler(
            self,
            lr_scheduler_type,
            optimizer,
            step_size=None,
            restart_step=None,
            multi_step=None
    ):
        """创建学习率衰减器
        Args:
            lr_scheduler_type: 衰减器类型
            optimizer: 优化器
            step_size: 使用StepLR时，必须指定该参数
        Return:
            my_lr_scheduler: 学习率衰减器
        """
        print('Creating lr scheduler: %s' % lr_scheduler_type)
        if lr_scheduler_type == 'StepLR':
            if not step_size:
                raise ValueError('You must specified step_size when you are using StepLR.')
            my_lr_scheduler = lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=0.1)
        elif lr_scheduler_type == 'CosineLR':
            if not restart_step:
                raise ValueError('You must specified restart_step when you are using CosineLR.')
            my_lr_scheduler = lr_scheduler.CosineAnnealingLR(optimizer, restart_step)
        elif lr_scheduler_type == 'MultiStepLR':
            if not multi_step:
                raise ValueError('You must specified multi step when you are using MultiStepLR.')
            my_lr_scheduler = lr_scheduler.MultiStepLR(optimizer, multi_step)            
        elif lr_scheduler_type == 'ReduceLR':
            my_lr_scheduler = lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5)
        elif lr_scheduler_type == 'CyclicLR':
            # 当使用Adam算法时，必须将cycle_momentum设置为False，默认为True；作者建议设定step_size_up = (2-8) x (training iterations in epoch)
            my_lr_scheduler = lr_scheduler.CyclicLR(optimizer, base_lr=1e-4, max_lr=2.6e-3, step_size_up=1805,
                                                    cycle_momentum=False)
        return my_lr_scheduler

    def load_chekpoint(self, model, weight_path):
        print('Loading weight from %s.' % weight_path)
        weight = torch.load(weight_path)
        model.load_state_dict(weight['state_dict'])
        return model
