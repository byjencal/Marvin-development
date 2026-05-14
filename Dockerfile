FROM yahboomtechnology/ros-foxy:3.5.3

WORKDIR /root/marvin

COPY . .

COPY ./configurations/.bashrc /root/.bashrc

WORKDIR /root/marvin/marvin_ws

RUN find . -type f -exec touch {} +

RUN rm -rf build install log || true

CMD ["/bin/bash"]

