# Fedora 25
FROM fedora@sha256:322cb01bbca26972c98051bacd3ab8555cec059496d64d35ee78b15de9ea0d06
LABEL maintainer="Freedom of the Press Foundation"
LABEL description="image to sign rpms in"
ARG FEDORA_PKGR_VER

RUN echo "${FEDORA_PKGR_VER}"

# sudo will be required for rpm --import of a pubkey
RUN dnf update -y && \
    dnf install -y \
    fedora-packager-${FEDORA_PKGR_VER}.noarch \
    make \
    rpm-sign \
    sudo \
    gnupg2 \
    python3-cryptography \
    python3-devel \
    python3-requests \
    python3-setuptools \
    vim && \
    yum clean all

ENV HOME /home/circleci
RUN useradd --create-home --home-dir $HOME circleci \
    && chown -R circleci:circleci $HOME && \
    echo "circleci ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR $HOME

USER circleci

CMD ["/usr/bin/bash"]
