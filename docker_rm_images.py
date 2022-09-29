# pylint: disable=print-used
import docker

cli = docker.from_env()


def rm_images():
    images = cli.images.list()
    for i in images:
        try:
            print("Deleting docker image %s" % i)
            cli.images.remove(i.id, force=True)
        except docker.errors.APIError as e:
            print("...image not deleted: %s" % e)


def main():
    rm_images()


if __name__ == "__main__":
    main()
