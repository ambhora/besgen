cmake_minimum_required(VERSION 3.25)
project(__PROJECT__ VERSION 0.1.0 LANGUAGES NONE)

include(CTest)
include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/besa/besaConfig.cmake")
include(cmake/features.cmake)
include(cmake/external.cmake)

besa_configure_complete()

besa_add_subdirectory(DIRECTORY src/cpp TYPE cpp)

if(BUILD_TESTING)
  besa_test_add_directory(
    NAME tests/unit
    PREFIX __PROJECT__
    TARGET_LIST __PROJECT__::lib__PROJECT__
    LABELS unit
  )
endif()
