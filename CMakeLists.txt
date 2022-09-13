cmake_minimum_required (VERSION 3.8)

project ("docker-build-ci")

add_executable (docker-build-ci "main.cpp" )

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET docker-build-ci PROPERTY CXX_STANDARD 20)
endif()
