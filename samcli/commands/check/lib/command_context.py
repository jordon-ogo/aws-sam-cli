import os
import functools

import click
import boto3

from samtranslator.translator.managed_policy_translator import ManagedPolicyLoader
from samtranslator.translator.translator import Translator
from samtranslator.public.exceptions import InvalidDocumentException
from samtranslator.parser import parser
from boto3.session import Session

from samcli.commands.local.cli_common.user_exceptions import SamTemplateNotFoundException
from samcli.yamlhelper import yaml_parse

from samcli.lib.replace_uri.replace_uri import _replace_local_codeuri as external_replace_local_codeuri
from ..exceptions import InvalidSamDocumentException


class CheckContext:
    def __init__(self, ctx, template_path):
        self.ctx = ctx
        self.template_path = template_path

    def run(self):
        converted_template = self.transform_template()

        click.echo("... analyzing application template")

    def transform_template(self):
        """
        Takes a sam template or a CFN json template and converts it into a CFN yaml template
        """
        managed_policy_map = self.load_policies()
        original_template = self._read_sam_file()

        updated_template = external_replace_local_codeuri(original_template)

        sam_translator = Translator(
            managed_policy_map=managed_policy_map,
            sam_parser=parser.Parser(),
            plugins=[],
            boto_session=Session(profile_name=self.ctx.profile, region_name=self.ctx.region),
        )

        # Translate template
        try:
            converted_template = sam_translator.translate(sam_template=updated_template, parameter_values={})
        except InvalidDocumentException as e:
            raise InvalidSamDocumentException(
                functools.reduce(lambda message, error: message + " " + str(error), e.causes, str(e))
            ) from e

        return converted_template

    def load_policies(self):
        """
        Load user policies from iam account
        """
        iam_client = boto3.client("iam")
        return ManagedPolicyLoader(iam_client).load()

    def _read_sam_file(self):
        """
        Reads the file (json and yaml supported) provided and returns the dictionary representation of the file.

        :param str template: Path to the template file
        :return dict: Dictionary representing the SAM Template
        :raises: SamTemplateNotFoundException when the template file does not exist
        """

        if not os.path.exists(self.template_path):
            click.secho("SAM Template Not Found", bg="red")
            raise SamTemplateNotFoundException("Template at {} is not found".format(self.template_path))

        with click.open_file(self.template_path, "r", encoding="utf-8") as sam_template:
            sam_template = yaml_parse(sam_template.read())

        return sam_template
