import docker


cli = docker.from_env()
images = cli.images.list()


for i in images:
    try:
        # cli.remove_image(i.id)
        print("Deleting docker image %s" % i) 
        cli.images.remove(i.id)
    except docker.errors.APIError as e:
        print("...image not deleted: %s" % e)
        pass
