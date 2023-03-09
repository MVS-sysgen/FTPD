FROM mainframed767/mvsce:2.0.1 as ftpd_objects
# Install rdrprep
RUN unset LD_LIBRARY_PATH && apt-get update && apt-get install -yq git build-essential python3-pip 
WORKDIR /build
ADD source/build /build/
ADD source/hlasm/ /build/hlasm/
RUN pip3 install ebcdic
RUN python3 generate_ftpdrakf.py ./hlasm
RUN python3 -u autobuild.py --objects -d -m /MVSCE

FROM mainframed767/jcc:wine as compiler
# With the objects we can compile ftpd.c
WORKDIR /
COPY source/c/ /c/
COPY --from=ftpd_objects /build/ftpdrakf.punch /c/
COPY source/build/objscan_input.nam /c
WORKDIR /c
RUN wine /jcc/jcc.exe -I/jcc/include -I/c -D__MVS_ -o -list=list.out /c/ftpd.c
RUN /jcc/objscan ftpdrakf.punch objscan_input.nam ftpdrac.obj
RUN /jcc/prelink -r /jcc/objs ftpd.load ftpd.obj ftpdrac.obj

FROM mainframed767/mvsce:2.0.1
RUN unset LD_LIBRARY_PATH && apt-get update && apt-get install -yq git build-essential python3-pip
WORKDIR /
RUN git clone --depth 1 https://github.com/mvslovers/rdrprep.git
WORKDIR /rdrprep
RUN make && make install
RUN pip3 install ebcdic requests
WORKDIR /XMI
COPY --from=ftpd_objects /MVSCE /MVSCE
COPY --from=compiler /c/ftpd.load /XMI/
COPY source/build/ /XMI/
COPY FTPD.conf /XMI/
RUN rdrprep link_ftpd.template
RUN python3 generate_install.py FTPD.conf
RUN python3 -u autobuild.py -d -m /MVSCE
RUN cp install.jcl \#001JCL.jcl
RUN python3 -u /MVSCE/MVP/extras/package_release.py --xmi-files FTPD.XMI --task-files \#001JCL.jcl --mvsce /MVSCE --name ./FTPD.MVP
WORKDIR /artifacts
RUN mv /XMI/FTPD.XMI /artifacts && mv /XMI/install.jcl /artifacts && mv /XMI/FTPD.MVP /artifacts
