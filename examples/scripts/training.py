import argparse
import importlib
import logging
import os

import numpy as np
import torch

from pythae.data.preprocessors import DataProcessor
from pythae.models import RHVAE
from pythae.models.rhvae import RHVAEConfig
from pythae.pipelines import TrainingPipeline
from pythae.trainers import BaseTrainingConfig

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
logger.addHandler(console)
logger.setLevel(logging.INFO)

PATH = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser()

# Training setting
ap.add_argument(
    "--dataset",
    type=str,
    default='mnist',
    choices=['mnist', 'cifar10', 'celeba'],
    help="The data set to use to perform training. It must be located in the folder 'data' at the "
    "path 'data/datset_name/' and contain a 'train_data.npz' and a 'eval_data.npz' file with the "
    "data being under the key 'data'. The data must be in the range [0-255] and shaped with the "
    "channel in first position (im_channel x height x width).",
    required=True,
)
ap.add_argument(
    "--model_name",
    help="The name of the model to train",
    choices=['ae', 'vae', 'beta_vae', 'wae', 'vamp', 'hvae', 'rhvae'],
    required=True
)
ap.add_argument(
    "--model_config",
    help="path to model config file (expected json file)",
    default=None
)
ap.add_argument(
    "--training_config",
    help="path to training config_file (expected json file)",
    default=os.path.join(PATH, "configs/base_training_config.json"),
)

args = ap.parse_args()

def main(args):

    if args.dataset == 'mnist':

        from pythae.models.nn.benchmarks.mnist import Encoder_AE_MNIST as Encoder_AE
        from pythae.models.nn.benchmarks.mnist import Encoder_VAE_MNIST as Encoder_VAE
        from pythae.models.nn.benchmarks.mnist import Decoder_AE_MNIST as Decoder_AE

    elif args.dataset == 'cifar10':

        from pythae.models.nn.benchmarks.cifar import Encoder_AE_CIFAR as Encoder_AE
        from pythae.models.nn.benchmarks.cifar import Encoder_VAE_CIFAR as Encoder_VAE
        from pythae.models.nn.benchmarks.cifar import Decoder_AE_CIFAR as Decoder_AE

    elif args.dataset == 'celeba':

        from pythae.models.nn.benchmarks.celeba import Encoder_AE_CELEBA as Encoder_AE
        from pythae.models.nn.benchmarks.celeba import Encoder_VAE_CELEBA as Encoder_VAE
        from pythae.models.nn.benchmarks.celeba import Decoder_AE_CELEBA as Decoder_AE

    try:
        logger.info(f'\nLoading {args.dataset} data...\n')
        train_data = np.load(
            os.path.join(PATH, f'data/{args.dataset}', 'train_data.npz'))['data'] / 255.
        eval_data = np.load(
            os.path.join(PATH, f'data/{args.dataset}', 'eval_data.npz'))['data'] / 255.
    except Exception as e:
        raise FileNotFoundError(
            f"Unable to load the data from 'data/{args.dataset}' folder. Please check that both a "
            "'train_data.npz' and 'eval_data.npz' are present in the folder.\n Data must be "
            " under the key 'data', in the range [0-255] and shaped with channel in first "
            "position\n"
            f"Exception raised: {type(e)} with message: " + str(e)
        ) from e

    logger.info('Successfully loaded data !\n')
    logger.info('------------------------------------------------------------')
    logger.info('Dataset \t \t Shape \t \t \t Range')
    logger.info(f'{args.dataset.upper()} train data: \t {train_data.shape} \t [{train_data.min()}-{train_data.max()}] ')
    logger.info(f'{args.dataset.upper()} eval data: \t {eval_data.shape} \t [{eval_data.min()}-{eval_data.max()}]')
    logger.info('------------------------------------------------------------\n')

    data_input_dim = tuple(train_data.shape[1:])

    if args.model_name == 'ae':
        from pythae.models import AE, AEConfig

        if args.model_config is not None:
            model_config = AEConfig.from_json_file(args.model_config)

        else:
            model_config = AEConfig()

        model_config.input_dim = data_input_dim
        
        model = AE(
            model_config=model_config,
            encoder=Encoder_AE(model_config),
            decoder=Decoder_AE(model_config)
        )

    elif args.model_name == 'vae':
        from pythae.models import VAE, VAEConfig

        if args.model_config is not None:
            model_config = VAEConfig.from_json_file(args.model_config)

        else:
            model_config = VAEConfig()

        model_config.input_dim = data_input_dim

        model = VAE(
            model_config=model_config,
            encoder=Encoder_VAE(model_config),
            decoder=Decoder_AE(model_config)
        )

    elif args.model_name == 'wae':
        from pythae.models import WAE_MMD, WAE_MMD_Config

        if args.model_config is not None:
            model_config = WAE_MMD_Config.from_json_file(args.model_config)

        else:
            model_config = WAE_MMD_Config()

        model_config.input_dim = data_input_dim

        model = WAE_MMD(
            model_config=model_config,
            encoder=Encoder_AE(model_config),
            decoder=Decoder_AE(model_config)
        )

    elif args.model_name == 'vamp':
        from pythae.models import VAMP, VAMPConfig

        if args.model_config is not None:
            model_config = VAMPConfig.from_json_file(args.model_config)

        else:
            model_config = VAMPConfig()

        model_config.input_dim = data_input_dim

        model = VAMP(
            model_config=model_config,
            encoder=Encoder_VAE(model_config),
            decoder=Decoder_AE(model_config)
        )

    elif args.model_name == 'beta_vae':
        from pythae.models import BetaVAE, BetaVAEConfig

        if args.model_config is not None:
            model_config = BetaVAEConfig.from_json_file(args.model_config)

        else:
            model_config = BetaVAEConfig()

        model_config.input_dim = data_input_dim

        model = BetaVAE(
            model_config=model_config,
            encoder=Encoder_VAE(model_config),
            decoder=Decoder_AE(model_config)
        )

    elif args.model_name == 'hvae':
        from pythae.models import HVAE, HVAEConfig

        if args.model_config is not None:
            model_config = HVAEConfig.from_json_file(args.model_config)

        else:
            model_config = HVAEConfig()

        model_config.input_dim = data_input_dim

        model = HVAE(
            model_config=model_config,
            encoder=Encoder_VAE(model_config),
            decoder=Decoder_AE(model_config)
        )

    elif args.model_name == 'rhvae':
        from pythae.models import RHVAE, RHVAEConfig

        if args.model_config is not None:
            model_config = RHVAEConfig.from_json_file(args.model_config)

        else:
            model_config = RHVAEConfig()

        model_config.input_dim = data_input_dim

        model = RHVAE(
            model_config=model_config,
            encoder=Encoder_VAE(model_config),
            decoder=Decoder_AE(model_config)
        )

    logger.info(f'Successfully build {args.model_name.upper()} model !\n')

    encoder_num_param = sum(p.numel() for p in model.encoder.parameters() if p.requires_grad)
    decoder_num_param = sum(p.numel() for p in model.decoder.parameters() if p.requires_grad)
    total_num_param = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info('----------------------------------------------------------------------')
    logger.info('Model \t Encoder params \t Decoder params \t Total params')
    logger.info(f"{args.model_name.upper()} \t {encoder_num_param} \t \t {decoder_num_param}"
    f" \t \t {total_num_param}")
    logger.info('----------------------------------------------------------------------\n')
    

    training_config = BaseTrainingConfig.from_json_file(args.training_config)

    pipeline = TrainingPipeline(
        training_config=training_config,
        model=model
    )

    pipeline(
        train_data=train_data,
        eval_data=eval_data
    )


if __name__ == "__main__":

    main(args)