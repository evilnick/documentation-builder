# Core modules
from glob import glob
from os import path
from shutil import rmtree
from unittest import TestCase

# Third party modules
from bs4 import BeautifulSoup
from git import Repo

# Local modules
from ubuntudesign.documentation_builder.builder import Builder


fixtures_path = path.join(path.dirname(__file__), 'fixtures')


"""
Most of the builder's actual operations should be tested in
test_operations.py, so hopefully we don't need to test every
permutation.

However, here we will try to test at the basic level the overall
function of the builder.
"""

def test_basic_build():
    base = path.join(fixtures_path, 'builder', 'base')
    output = path.join(fixtures_path, 'builder', 'output')
    expected_output = path.join(fixtures_path, 'builder', 'output_basic')
    if path.exists(output):
        rmtree(output)

    Builder(
        base_directory=base,
        output_path=output,
        quiet=True
    )

    _compare_trees(output, expected_output)
    _compare_html_parts(output, expected_output)

    rmtree(output)


def test_custom_template():
    base = path.join(fixtures_path, 'builder', 'base')
    output = path.join(fixtures_path, 'builder', 'output')
    template_path = path.join(fixtures_path, 'builder', 'template.jinja2')
    expected_output = path.join(
        fixtures_path, 'builder', 'output_custom_template'
    )
    if path.exists(output):
        rmtree(output)

    Builder(
        base_directory=base,
        output_path=output,
        template_path=template_path,
        quiet=True
    )

    _compare_trees(output, expected_output)
    _compare_html_parts(output, expected_output)

    rmtree(output)


def test_source_folder():
    base = path.join(fixtures_path, 'builder', 'base-source-folder')
    output = path.join(fixtures_path, 'builder', 'output')
    expected_output = path.join(
        fixtures_path, 'builder', 'output_basic'
    )
    if path.exists(output):
        rmtree(output)

    Builder(
        base_directory=base,
        source_folder='./src',
        output_path=output,
        quiet=True
    )

    _compare_trees(output, expected_output)
    _compare_html_parts(output, expected_output)

    rmtree(output)


def test_versions():
    base = path.join(fixtures_path, 'builder', 'base-repo')
    output = path.join(fixtures_path, 'builder', 'output')
    expected_output = path.join(
        fixtures_path, 'builder', 'output_versions'
    )

    # make sure things don't exist
    if path.exists(output):
        rmtree(output)
    if path.exists(base):
        rmtree(base)

    # Clone repository and pull down all branches
    repo = Repo.clone_from(
        (
            'https://github.com/CanonicalLtd/'
            'documentation-builder-test-builder-repo.git'
        ),
        base
    )
    origin = repo.remotes.origin
    repo.create_head('1.0', origin.refs['1.0'])
    repo.create_head('latest', origin.refs['latest'])

    Builder(
        base_directory=base,
        output_path=output,
        build_version_branches=True,
        quiet=True
    )

    _compare_trees(output, expected_output)
    _compare_html_parts(output, expected_output)

    rmtree(output)
    rmtree(base)


def test_output_media_path():
    base = path.join(fixtures_path, 'builder', 'base')
    output = path.join(fixtures_path, 'builder', 'output')
    output_media_path = path.join(
        fixtures_path, 'builder', 'output', 'files', 'media'
    )
    expected_output = path.join(
        fixtures_path, 'builder', 'output_media_path'
    )
    if path.exists(output):
        rmtree(output)

    Builder(
        base_directory=base,
        output_path=output,
        output_media_path=output_media_path,
        quiet=True
    )

    _compare_trees(output, expected_output)
    _compare_html_parts(output, expected_output)

    rmtree(output)


def test_media_url():
    base = path.join(fixtures_path, 'builder', 'base')
    output = path.join(fixtures_path, 'builder', 'output')
    expected_output = path.join(
        fixtures_path, 'builder', 'output_media_url'
    )
    if path.exists(output):
        rmtree(output)

    Builder(
        base_directory=base,
        media_url='/static/media',
        output_path=output,
        quiet=True
    )

    _compare_trees(output, expected_output)
    _compare_html_parts(output, expected_output)

    rmtree(output)


def _compare_trees(directory_a, directory_b):
    a_files = []
    b_files = []
    for filepath in glob(path.join(directory_a, '**'), recursive=True):
        a_files.append(path.relpath(filepath, directory_a))
    for filepath in glob(path.join(directory_b, '**'), recursive=True):
        b_files.append(path.relpath(filepath, directory_b))

    assert sorted(a_files) == sorted(b_files)


def _compare_html_parts(directory_a, directory_b):
    for a_filepath in glob(
        path.join(directory_a, '**/*.html'),
        recursive=True
    ):
        local_filepath = path.relpath(a_filepath, directory_a)
        b_filepath = path.join(directory_b, local_filepath)

        with open(a_filepath, encoding="utf-8") as a_file:
            a_soup = BeautifulSoup(a_file.read(), 'html.parser')
        with open(b_filepath, encoding="utf-8") as b_file:
            b_soup = BeautifulSoup(b_file.read(), 'html.parser')

        # Compare titles
        a_title = a_soup.select('head title')[0].contents
        b_title = b_soup.select('head title')[0].contents
        assert a_title == b_title

        # Compare links
        a_links = (
            a_soup.select('.p-sidebar-nav a') + a_soup.select('main a')
        )
        b_links = (
            b_soup.select('.p-sidebar-nav a') + b_soup.select('main a')
        )

        for index, a_link in enumerate(a_links):
            b_link = b_links[index]
            assert a_link['href'] == b_link['href']
            assert a_link.contents == b_link.contents

        # Compare images
        a_imgs = a_soup.select('main img')
        b_imgs = b_soup.select('main img')

        for index, a_img in enumerate(a_imgs):
            b_img = b_imgs[index]
            assert a_img['src'] == b_img['src']
            assert a_img['alt'] == b_img['alt']
