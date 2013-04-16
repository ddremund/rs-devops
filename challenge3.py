#!/usr/bin/python -tt

   # Copyright 2013 Derek Remund (derek.remund@rackspace.com)

   # Licensed under the Apache License, Version 2.0 (the "License");
   # you may not use this file except in compliance with the License.
   # You may obtain a copy of the License at

   #     http://www.apache.org/licenses/LICENSE-2.0

   # Unless required by applicable law or agreed to in writing, software
   # distributed under the License is distributed on an "AS IS" BASIS,
   # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   # See the License for the specific language governing permissions and
   # limitations under the License.

import pyrax
import argparse
import os
import sys

def main():

	parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--container', help="Name of container to use/create.")
    parser.add_argument('-d', '--dir', default=os.path.dirname(os.path.realpath(__file__)), help="Directory to upload; defaults to the current directory.")

    args = parser.parse_args()

    

if __name__ == '__main__':
    main()