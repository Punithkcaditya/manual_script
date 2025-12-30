<template>
  <!-- Category Page (Search Results) -->
  <div v-if="isCategoryPage">
    <section
      class="relative bg-cover bg-center text-white h-[40em] sm:h-[45em] banner-responsive"
    >
      <!-- Semi-transparent black overlay -->
      <div class="absolute inset-0 bg-[#00000024] bg-opacity-40"></div>
      
      <div class="relative px-4 pt-[18em] md:pt-[16em] text-center">
        <h1 class="text-3xl lg:text-5xl leading-tight">
          Rent {{ dynamicCategoryName.toUpperCase() }} flat in <br/> 
          <span class="greeline font-bold ">{{ dynamicAreaName }}</span> 
        </h1>
        <div class="flex justify-center">
          <button
            type="button"
            class="bg-[#afa11e] text-white px-4 py-2 rounded-md mt-5 sm:mt-10"
            onclick="document.querySelector('#flats-available').scrollIntoView({ behavior: 'smooth' })"
          >
            See available flats
          </button>
        </div>
      </div>
    </section>
    
    <Suspense>
      <template #default>
        <HomePageCarousel
          backgroundColor="bg-[#f5f4e4]"
          dividerImage="assets/images/d-dashline.png"
          :bannerData="{
            features: [
              {
                title: 'Better Quality Flats',
                image: '/assets/images/verify-black.png',
                alt: 'verify',
              },
              {
                title: 'Better Maintained & Managed',
                image: '/assets/images/verify-black.png',
                alt: 'verify',
              },
              {
                title: 'Better Location',
                image: '/assets/images/verify-black.png',
                alt: 'verify',
              },
              {
                title: 'Better Value for Money',
                image: '/assets/images/verify-black.png',
                alt: 'verify',
              },
            ],
          }"
        />
      </template>
      <template #fallback>
        <div class="min-h-[200px] bg-[#f5f4e4] flex items-center justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#8a7c0a]"></div>
        </div>
      </template>
    </Suspense>
    
    <ClientOnly>
      <Suspense>
        <template #default>
          <FeaturesAtKotsLanding />
        </template>
        <template #fallback>
          <div class="min-h-[400px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>

    <Suspense>
      <template #default>
        <FlatsAvailableSection 
          :flats="flats" 
          :totalFlatCount="totalFlatCountFromCarousel" 
          @filtersChanged="handleFiltersChanged"
        />
      </template>
      <template #fallback>
        <div class="min-h-[400px] bg-white flex items-center justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      </template>
    </Suspense>

    <Suspense>
      <template #default>
        <PropertiesCarousel
          :nearLocation="`available near`"
          :location="slugToTitle(area)"
          apiEndpoint="/api/getPropertiesAndFlats"
          :limit="10"
          :initialData="propertiesCarouselData"
          @flatsLoaded="handleFlatsLoaded"
          @metadataLoaded="handleMetadataLoaded"
        />
      </template>
      <template #fallback>
        <div class="min-h-[400px] bg-white flex items-center justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      </template>
    </Suspense>
 
    <ClientOnly>
      <Suspense>
        <template #default>
          <TenantReviews />
        </template>
        <template #fallback>
          <div class="min-h-[300px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>

    <ClientOnly>
      <Suspense>
        <template #default>
          <MediaSpotlight />
        </template>
        <template #fallback>
          <div class="min-h-[300px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>

    <ClientOnly>
      <Suspense>
        <template #default>
          <KotsProjectsFaq />
        </template>
        <template #fallback>
          <div class="min-h-[300px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>

    <ClientOnly>
      <Suspense>
        <template #default>
          <KotsProjectsContactUs id="contact-section" />
        </template>
        <template #fallback>
          <div class="min-h-[300px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>

    <ClientOnly>
      <Suspense>
        <template #default>
          <Footer />
        </template>
        <template #fallback>
          <div class="min-h-[300px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>
    
    <!-- Mobile Footer - Fixed at bottom for mobile only -->
    <ClientOnly>
      <Suspense>
        <template #default>
          <MobileFooter :filterKey="filterKey" />
        </template>
        <template #fallback>
          <div class="min-h-[100px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>
  </div>
  
  <!-- Property Page -->
  <div v-if="showPropertySection" class="mt-10">
    <div class="ml-[1em] mb-2">
      <button
        @click="goBack"
        class="text-[#afa11e]  font-medium hover:underline flex items-center gap-1 ml-0 lg:ml-2 md:ml-0 text-[#AFA11E] font-['Open_Sans_Hebrew'] text-[14px] not-italic font-bold underline underline-offset-auto decoration-solid decoration-from-font"
      >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
  <path d="M12.6673 8H3.33398" stroke="#AFA11E" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M8.00065 12.6667L3.33398 8.00004L8.00065 3.33337" stroke="#AFA11E" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
</svg> Back
      </button>
    </div>
    <div
      class="breadcrumb d-flex gap-2 mobileBread text-[10px] md:text-[14px] text-[#999] mt-[1em] !flex !gap-2 ml-[2em]"
    >
      <a style="color: #505050" href="/" class="underline">Home</a>
      /
      <a
        style="color: #505050"
        href="/flats-for-rent-in-bangalore"
        class="underline"
        >Explore flats</a
      >
      /
      <a style="color: #505050" :href="`/bangalore/flats-for-rent-in-${property.area?.toLowerCase().replace(/\s+/g, '-')}`" class="underline">{{
        property.area
      }}</a>
      /
      <a style="color: #505050" href="#" class="text-black">{{
        property.title
      }}</a>
    </div>

    <div
      class="bg-[#ffffffe6] p-4 sm:p-8  max-w-md w-full lg:w-auto lg:absolute lg:top-[-7em] lg:right-[8em] lg:hidden"
      style="z-index: 10"
    >
      <h1 class="text-4xl font-bold mb-2">{{ property.title }}</h1>
      <!-- <p class="text-lg mb-4">{{ property.description }}</p> -->
      <p class="text-lg mb-4">
          Urban Gated Apartment in
          <span class="fw-bold text-dark"> {{ property.area }}</span>
        </p>
        <p class="my-[5px] text-[#666] text-[16px] font-bold">
          <span v-if="availableFlatTypes.length > 0">
            {{ availableFlatTypes.join(', ') }}
          </span>
          <span v-else>{{ property?.type }}</span>
        </p>
    </div>

    <div class="relative w-full mb-4 mt-4 sm:mb-8 sm:mt-8">
         <!-- Overlay Property Details Card -->
         <div
        class="bg-[#ffffffe6] p-4 sm:p-8 rounded-lg shadow-lg max-w-md w-full lg:w-auto lg:absolute lg:top-[-7em] lg:right-[3em] lg:block hidden"
        style="z-index: 10"
      >
        <h1 class="text-4xl font-bold mb-2">{{ property.title }}</h1>
        <p class="text-lg mb-4">
          Urban Gated Apartment in
          <span class="fw-bold text-dark"> {{ property.area }}</span>
        </p>
        <p class="my-[5px] text-[#666] text-[16px] font-bold">
          <span v-if="availableFlatTypes.length > 0">
            {{ availableFlatTypes.join(', ') }}
          </span>
          <span v-else>{{ property?.type }}</span>
        </p>
      </div>
      <!-- Main container for the image gallery -->
      <div
        class="w-full max-h-[560px] aspect-[4/3] overflow-hidden rounded-lg cursor-pointer"
        @click="openModal(currentImageIndex)"
      >
        <!-- Display YouTube video iframe if current item is a video -->
        <div
          v-if="getCurrentMediaItem().type === 'youtube'"
          class="relative w-full h-full"
        >
          <iframe
            :src="getCurrentMediaItem().url"
            :alt="metaTitleForAlt"
            :title="`Virtual tour of ${property.title}`"
            class="w-full h-full border-0"
            frameborder="0"
            allowfullscreen
            loading="lazy"
          ></iframe>
        </div>
        <!-- Display full quality image if current item is an image -->
        <img
          v-else
          :src="getCurrentMediaItem().url"
          :alt="metaTitleForAlt"
          width="1200"
          height="900"
          fetchpriority="high"
          loading="eager"
          decoding="async"
          class="img-property-main"
          style="image-orientation: from-image;"
        />
      </div>

      <!-- Carousel controls and thumbnails (always visible) -->
      <div
        class="flex items-center pt-10 sm:pt-20 pb-4 sm:pb-8 max-w-7xl mx-auto justify-start pl-5"
      >
        <div class="flex justify-between w-[90%]">
          <div class="flex items-center justify-center mb-2 p-2">
            <span
              class="text-[#292d32] font-light text-2xl italic text-[#292d32] font-light text-[50px] italic"
            >
              {{ currentImageIndex + 1 }}
            </span>
            <span class="text-[#505050] font-light text-xl italic">/</span>
            <span class="text-[#505050] font-light text-xl italic">
              {{ getTotalMediaCount() }}
            </span>
          </div>
          <div class="flex justify-start overflow-x-auto w-full gap-2 pl-5">
            <!-- Handle mixed media (images and videos) -->
            <template v-if="property.media">
              <div
                v-for="(mediaItem, index) in property.media"
                :key="`media-${index}`"
                class="relative"
              >
                <NuxtImg
                  :src="
                    mediaItem.type === 'youtube'
                      ? getYouTubeThumbnail(mediaItem.watchUrl || mediaItem.url)
                      : mediaItem.thumbUrl || mediaItem.url
                  "
                  :alt="metaTitleForAlt"
                  width="230"
                  height="230"
                  loading="lazy"
                  decoding="async"
                  class="img-property-thumbnail"
                  :class="
                    currentImageIndex === index
                      ? 'img-property-thumbnail-active'
                      : 'img-property-thumbnail-inactive'
                  "
                  @click="openModal(index)"
                  @error="handleImageError($event, mediaItem)"
                  style="image-orientation: from-image;"
                />
                <!-- Video icon overlay for YouTube videos -->
                <div
                  v-if="mediaItem.type === 'youtube'"
                  class="absolute inset-0 flex items-center justify-center pointer-events-none"
                >
                  <div
                    class="bg-red-600 rounded-full p-2 absolute top-[35%] left-1/2 -translate-x-1/2 -translate-y-1/2"
                  >
                    <NuxtImg
                      src="https://kots-world.b-cdn.net/Final/assets/images/video-square.png"
                      alt="video square"
                      width="16"
                      height="16"
                      loading="lazy"
                      decoding="async"
                      class="w-4 h-4"
                    />
                  </div>
                </div>
              </div>
            </template>
            <!-- Fallback for old image array structure -->
            <template v-else>
              <NuxtImg
                v-for="(img, index) in property.images"
                :key="`image-${index}`"
                :src="img"
                :alt="metaTitleForAlt"
                width="230"
                height="230"
                loading="lazy"
                decoding="async"
                class="img-thumbnail w-full md:w-[230px]"
                :class="
                  currentImageIndex === index
                    ? 'img-thumbnail-active'
                    : 'img-thumbnail-inactive'
                "
                @click="openModal(index)"
              />
            </template>
          </div>
        </div>
        <div class="flex">
          <button
            class="bg-[#f8f8f8] rounded-full w-8 h-8 flex justify-center items-center mr-2"
            @click.stop="previousImage"
          >
            <NuxtImg
              src="https://kots-world.b-cdn.net/Final/assets/images/pop-left.png"
              alt="pop left"
              width="24"
              height="24"
              loading="lazy"
              decoding="async"
              class="w-4 h-4"
            />
          </button>
          <button
            class="bg-[#f8f8f8] rounded-full w-8 h-8 flex justify-center items-center ml-2"
            @click.stop="nextImage"
          >
            <NuxtImg
              src="https://kots-world.b-cdn.net/Final/assets/images/pop-right.png"
              alt="pop right"
              width="24"
              height="24"
              loading="lazy"
              decoding="async"
              class="w-4 h-4"
            />
          </button>
        </div>
      </div>

   
    </div>

    <!-- Modal -->
    <div
      v-if="isModalOpen"
      class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50"
      @click="closeModal"
    >
      <div class="relative max-w-7l w-full mx-4 flex flex-col" @click.stop>
        <!-- Close button -->
        <button
          @click="closeModal"
          class="absolute top-4 right-4 text-white bg-black bg-opacity-50 hover:bg-opacity-70 rounded-full p-2 z-50 transition-colors"
        >
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>

        <!-- Main image/video container -->
        <div class="relative w-full flex items-center justify-center mb-4" style="max-height: 70vh;">
          <!-- Display YouTube video if current item is a video -->
          <div
            v-if="getCurrentMediaItem().type === 'youtube'"
            class="w-full h-full"
          >
            <iframe
              :src="getCurrentMediaItem().url + '?rel=0&showinfo=0&autoplay=1'"
              :alt="metaTitleForAlt"
              :title="`Virtual tour of ${property.title}`"
              class="w-full h-full rounded-lg"
              frameborder="0"
              allow="autoplay; fullscreen"
              style="min-height: 400px"
            ></iframe>
          </div>
          <!-- Display full quality image if current item is an image -->
          <NuxtImg
            v-else
            :src="getCurrentMediaItem().url"
            :alt="metaTitleForAlt"
            width="1200"
            height="900"
            loading="lazy"
            decoding="async"
            class="img-property-modal"
          />

          <!-- Navigation buttons -->
          <button
            v-if="getTotalMediaCount() > 1"
            @click="previousImage"
            class="absolute left-4 top-1/2 transform -translate-y-1/2 text-white bg-black bg-opacity-50 hover:bg-opacity-70 rounded-full p-3 transition-colors z-10"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 19l-7-7 7-7"
              ></path>
            </svg>
          </button>

          <button
            v-if="getTotalMediaCount() > 1"
            @click="nextImage"
            class="absolute right-4 top-1/2 transform -translate-y-1/2 text-white bg-black bg-opacity-50 hover:bg-opacity-70 rounded-full p-3 transition-colors z-10"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              ></path>
            </svg>
          </button>

          <!-- Media counter -->
          <div
            class="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-white bg-black bg-opacity-50 px-4 py-2 rounded-full z-10"
          >
            {{ currentImageIndex + 1 }} / {{ getTotalMediaCount() }}
          </div>
        </div>

        <!-- Thumbnail navigation - positioned below video -->
        <div class="flex justify-center gap-2 max-w-md mx-auto overflow-x-auto pb-4">
          <!-- Handle mixed media (images and videos) -->
          <template v-if="property.media">
            <div
              v-for="(mediaItem, index) in property.media"
              :key="`modal-media-${index}`"
              class="relative flex-shrink-0 w-16 h-16 overflow-hidden rounded cursor-pointer border-2 transition-all"
              :class="
                currentImageIndex === index
                  ? 'border-white'
                  : 'border-transparent opacity-70 hover:opacity-100'
              "
              @click="currentImageIndex = index"
            >
              <NuxtImg
                :src="
                  mediaItem.type === 'youtube'
                    ? getYouTubeThumbnail(mediaItem.watchUrl || mediaItem.url)
                    : mediaItem.thumbUrl || mediaItem.url
                "
                :alt="metaTitleForAlt"
                width="64"
                height="64"
                loading="lazy"
                decoding="async"
                class="img-property-full"
                @error="handleImageError($event, mediaItem)"
              />
              <!-- Video icon overlay for YouTube videos -->
              <div
                v-if="mediaItem.type === 'youtube'"
                class="absolute inset-0 flex items-center justify-center pointer-events-none"
              >
                <div class="bg-red-600 rounded-full p-1">
                  <svg
                    class="w-4 h-4 text-white"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
              </div>
            </div>
          </template>
          <!-- Fallback for old image array structure -->
          <template v-else>
            <div
              v-for="(img, index) in property.images"
              :key="`modal-image-${index}`"
              class="flex-shrink-0 w-16 h-16 overflow-hidden rounded cursor-pointer border-2 transition-all"
              :class="
                currentImageIndex === index
                  ? 'border-white'
                  : 'border-transparent opacity-70 hover:opacity-100'
              "
              @click="currentImageIndex = index"
            >
              <NuxtImg
                :src="img"
                :alt="metaTitleForAlt"
                width="64"
                height="64"
                loading="lazy"
                decoding="async"
                class="img-property-full"
              />
            </div>
          </template>
        </div>
      </div>
    </div>
    <!-- tab section start -->
    <div class="min-h-screen bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Left Column - Content -->
          <div class="lg:col-span-2">
            <!-- Navigation Tabs -->
            <div class="flex flex-wrap gap-3 sm:gap-6 mb-8 items-center">
              <a
                v-for="tab in tabs"
                :key="tab.id"
                :href="'#' + tab.id"
                class="px-4 py-2 sm:px-6 sm:py-3 rounded-full text-sm font-medium transition-colors hover:bg-gray-100 text-black border-2 border-[#f8f8f8] text-[14px] sm:text-[16px] px-[16px] sm:px-[20px] py-[8px] sm:py-[10px] lg:rounded-[50px] rounded-[10px] w-fit font-normal cursor-pointer flex-shrink-0"
                :class="{ 'text-white bg-[#292d32]': activeSection === tab.id }"
                @click.prevent="scrollToSection(tab.id)"
              >
                {{ tab.label }}
              </a>
            </div>

            <!-- About Section -->
            <!-- {{ furnishing.filter(f => f.label !== 'Furnishing').map(f => f.label).join(' & ') }} -->
            <div :id="'about'" class="bg-white rounded-lg p-6 mb-8">
              <h2
                class="text-2xl font-bold mb-4 border-b-2 border-[#f4f4f4] pb-[10px]"
              >
              About: {{ availableFlatTypes.join(' & ') }} Flats for Rent:  {{ formatPropertyTitle(property?.title) || "Kots Abode" }}
              </h2>
              <p class="text-gray-600 leading-relaxed">
                {{
                  showFullAbout
                    ? property?.locationDescription || aboutFull
                    : getAboutPreview()
                }}
                <button
                  class="text-blue-600 hover:underline ml-1"
                  @click="showFullAbout = !showFullAbout"
                >
                  {{ showFullAbout ? "See less" : "See more" }}
                </button>
              </p>
            </div>

            <!-- Property Features Section -->
            <div :id="'property-features'" class="bg-white rounded-lg p-6 mb-8">
              <h2
                class="text-2xl font-bold mb-8 border-b-2 border-[#f4f4f4] my-[2em] font-bold"
              >
                Property Features of {{ toTitleCase(property?.title) }} :   {{ availableFlatTypes.join(', ') }}
              </h2>

              <!-- Loading State -->
              <div
                v-if="amenitiesLoading"
                class="flex justify-center items-center py-8"
              >
                <div
                  class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#afa11e]"
                ></div>
                <span class="ml-2 text-gray-600">Loading amenities...</span>
              </div>

              <!-- Dynamic Amenities - Mobile: Horizontal Scroll, Desktop: Grid -->
              <div
                v-else
                class="overflow-x-auto sm:overflow-x-visible"
              >
                <!-- Mobile: Horizontal scroll -->
                <div class="flex gap-6 pb-4 sm:hidden min-w-max">
                  <div
                    v-for="(amenity, index) in amenities"
                    :key="index"
                    class="flex flex-col items-center text-center flex-shrink-0 w-24"
                    :title="amenity.description"
                  >
                    <div
                      class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-4"
                    >
                      <NuxtImg
                        :src="amenity.image"
                        :alt="metaTitleForAlt"
                        width="90"
                        height="90"
                        loading="lazy"
                        decoding="async"
                        class="max-w-[90px]"
                      />
                    </div>
                    <h3
                      class="mb-2 text-center text-[#505050] font-light text-[14px] leading-tight"
                    >
                      {{ amenity.title }}
                    </h3>
                  </div>
                </div>
                
                <!-- Desktop: Grid layout -->
                <div class="hidden sm:grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
                  <div
                    v-for="(amenity, index) in amenities"
                    :key="index"
                    class="flex flex-col items-center text-center border-r-2 border-r-[#f4f4f4] last:border-r-0"
                    :title="amenity.description"
                  >
                    <div
                      class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-4"
                    >
                      <NuxtImg
                        :src="amenity.image"
                        :alt="metaTitleForAlt"
                        width="90"
                        height="90"
                        loading="lazy"
                        decoding="async"
                        class="max-w-[90px]"
                      />
                    </div>
                    <h3
                      class="mb-2 text-start text-[#505050] font-light text-[16px]"
                    >
                      {{ amenity.title }}
                    </h3>
                  </div>
                </div>
              </div>

              <!-- Error State / Fallback Message -->
              <div
                v-if="!amenitiesLoading && amenities.length === 0"
                class="text-center py-8"
              >
                <p class="text-gray-600">
                  Unable to load amenities at this time.
                </p>
              </div>
            </div>

            <!-- Virtual Tour Section -->
            <div v-if="property?.virtualTour" :id="'virtual-tour'" class="bg-white rounded-lg p-6 mb-8">
              <h2 class="text-2xl font-bold mb-4">Virtual Tour {{ toTitleCase(property?.title) }} :   {{ availableFlatTypes.join(', ') }}</h2>
              <div class="bg-gray-50">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                  <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <!-- Left Column - Content -->
                    <div class="lg:col-span-3">
                      <!-- Virtual Tour Section -->
                      <iframe
                        :src="property.virtualTour"
                  :alt="metaTitleForAlt"
                  :title="`Virtual tour of ${property.title}`"
                        width="100%"
                        height="435"
                        class="border-0 map-radius"
                        allowfullscreen=""
                        loading="lazy"
                  importance="low"
                      ></iframe>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Location Section -->
            <div :id="'location'" class="bg-white rounded-lg p-6 mb-8">
              <div class="aspect-video rounded-lg items-center justify-center">
                <h3
                  class="border-b-2 border-b-[#f4f4f4] font-bold text-[24px] mb-[20px] md:mb-[40px]"
                >
                  Location of {{ toTitleCase(property?.title) }} :   {{ availableFlatTypes.join(', ') }}
                </h3>
                <p class="text-[#505050] font-light text-[16px]">
                  {{
                    property?.localityDescription ||
                    "KOTS Abode is a premium living space offering studio flats and 1BHK for rent in Maithri layout locality that is ready to move in. These 1BHK homes are better-q"
                  }}
                </p>
                <iframe
                  :src="
                    property?.mapDescription ||
                    'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d242.98793121920667!2d77.75541105766222!3d12.984199244529485!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bae0f579782834b%3A0x71e65975268b390c!2sKots%20Abode!5e0!3m2!1sen!2sin!4v1705487000124!5m2!1sen!2sin'
                  "
                  :alt="metaTitleForAlt"
                  :title="`Location map of ${property.title}`"
                  width="100%"
                  class="border-0 map-radius h-[300px] md:h-[548px]"
                  allowfullscreen=""
                  loading="lazy"
                  importance="low"
                ></iframe>
                <!-- <div class="mt-3">
                  {{
                    property?.locationDescription ||
                    "Located on the 2nd Main Road in Maithri layout, Whitefield Kots Abode offers 1BHK and 2bhk for rent in Whitefield, enabling a premium living experience for its tenants. The property is near tech parks like Brigade Metropoli (2km), Bagmane Constellation (2km), Brigade Southfield (0.5km), ITPL and Prestige Shantiniketan (3.5km). The closest metro station is 0.8km away from Kots Abode. Popular restaurants and microbreweries like Biergarten are located within a 0.6km radius. Families Supermarket is located 0.4km away from the property."
                  }}
                </div> -->
              </div>
            </div>
          </div>

          <!-- Right Column - Property Card (Desktop Only) -->
          <div class="hidden lg:block lg:col-span-1">
            <div class="bg-white rounded-lg p-6 shadow-sm sticky top-10 max-h-[calc(100vh-1rem)] overflow-auto">
              <h1 class="text-2xl md:text-3xl lg:text-[36px] xl:text-[46px] mb-[10px] font-bold leading-tight">
                {{ property?.title || "KOTS ABODE" }}
              </h1>
              <p class="my-[5px] text-[#505050] font-bold text-[16px]">
                <span v-if="availableFlatTypes.length > 0">
                  {{ availableFlatTypes.join(', ') }}
                </span>
                <span v-else>{{ property?.type || "1 BHK - 2 BHK" }}</span>
              </p>
              <p class="text-gray-600 mb-6">
                {{ property?.location || property?.localityDescription || property?.area  || "Whitefield" }}
              </p>

              <div class="mb-6">
                <p class="text-sm text-gray-600 mb-2">From</p>
                <p class="text-3xl font-bold">
                  {{ property?.rent || "₹ 32,800/mo." }}
                </p>
                <p class="text-sm text-gray-600 mt-2">
                  *Security deposit will be 2 months of rent.
                </p>
              </div>

              <button
                class="w-full bg-[#afa11e] hover:bg-[#afa11e]/80 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
                @click="scrollToFlats"
              >
                Show {{ totalAvailableFlats !== null && totalAvailableFlats !== undefined ? totalAvailableFlats : (property?.flats?.length || 0) }} flats
                <svg
                  class="w-5 h-5 ml-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- tab section end -->

    <!-- flats available section start -->
    <div class="bg-[#f7f7e8] py-12" id="flats-available">
      <div class="max-w-7xl mx-auto px-4">
        <div
          class="mb-6 flex flex-col md:flex-row md:items-center md:justify-between"
        >
          <div>
            <span class="text-lg text-[#505050]"
              >{{ totalAvailableFlats !== null && totalAvailableFlats !== undefined ? totalAvailableFlats : availableFlats.length }} rental flats available in</span
            >
            <h2 class="text-xl font-bold text-[#292d32] leading-tight max-w-[24em]">
               {{ formatPropertyTitle(property?.title) || "Kots Abode" }}
            </h2>
          </div>
          <div class="flex flex-wrap gap-3 mt-4 md:mt-0">
            <!-- Clear Filter Button -->
            <button
              v-if="hasActiveFilters"
              @click="resetToDefaults"
              class="px-4 py-2 text-sm font-medium text-[oklch(0.7_0.14_102.75)] hover:text-red-700 hover:bg-red-50 border hover:border-red-50 border-[oklch(0.7_0.14_102.75)] rounded-lg transition-colors flex items-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
              Clear Filters
            </button>
            <div class="relative inline-block text-left">
              <!-- Dropdown Trigger -->
              <button
                @click="isOpenLocality = !isOpenLocality"
                class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:border-olive transition-colors bg-white"
              >
                <span class="text-black font-bold text-[14px]">{{
                  selected || "Flat Type"
                }}</span>
                <NuxtImg
                  src="https://kots-world.b-cdn.net/Final/assets/images/arrow-circle-down.png"
                  alt="arrow circle down"
                  width="16"
                  height="16"
                  loading="lazy"
                  decoding="async"
                  class="img-dropdown-icon"
                  :class="[
                    isOpenLocality ? 'img-rotate-180' : 'img-rotate-0',
                  ]"
                />
              </button>

              <!-- Dropdown List -->
              <ul
                v-if="isOpenLocality"
                class="absolute mt-2 w-[9em] bg-white border border-gray-200 rounded-lg shadow-lg z-10"
              >
                <li
                  v-for="(loc, index) in localities"
                  :key="index"
                  @click="selectLocality(loc.label)"
                  class="px-4 py-2 cursor-pointer text-sm border-b border-gray-100 hover:bg-gray-100"
                  :class="{
                    'bg-gray-800 text-white font-semibold':
                      selected === loc.label,
                  }"
                >
                  {{ loc.label }}
                </li>
              </ul>
            </div>
            <!-- Date Picker -->
            <div class="relative inline-block text-left">
              <button
                @click="isOpenDatePicker = !isOpenDatePicker"
                class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:border-olive transition-colors bg-white"
              >
                <span class="text-black font-bold text-[14px]">{{ dateDisplayLabel }}</span>
                <NuxtImg
                  src="https://kots-world.b-cdn.net/Final/assets/images/arrow-circle-down.png"
                  alt="arrow circle down"
                  width="16"
                  height="16"
                  loading="lazy"
                  decoding="async"
                  class="img-dropdown-icon"
                  :class="[
                    isOpenDatePicker ? 'img-rotate-180' : 'img-rotate-0',
                  ]"
                />
              </button>
              
              <div
                v-if="isOpenDatePicker"
                class="absolute mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 left-0 right-0 md:left-auto md:right-0 md:w-auto"
              >
                <Datepicker 
                  v-model="selectedDate" 
                  inline
                  :auto-apply="true" 
                  :enable-time-picker="false" 
                  :min-date="new Date()"
                  @update:model-value="dateFilterActive = true; isOpenDatePicker = false"
                />
              </div>
            </div>

            <div class="relative inline-block text-left">
              <!-- Dropdown Trigger -->
              <button
                @click="isOpenFurnishing = !isOpenFurnishing"
                class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:border-olive transition-colors bg-white"
              >
                <span class="text-black font-bold text-[14px]">{{
                  selectedFurnishing || "Furnishing"
                }}</span>
                <NuxtImg
                  src="https://kots-world.b-cdn.net/Final/assets/images/arrow-circle-down.png"
                  alt="arrow circle down"
                  width="16"
                  height="16"
                  loading="lazy"
                  decoding="async"
                  class="img-dropdown-icon"
                  :class="[
                    isOpenFurnishing ? 'img-rotate-180' : 'img-rotate-0',
                  ]"
                />
              </button>

              <!-- Dropdown List -->
              <ul
                v-if="isOpenFurnishing"
                class="absolute mt-2 w-[9em] bg-white border border-gray-200 rounded-lg shadow-lg z-10"
              >
                <li
                  v-for="(locfur, index) in furnishing"
                  :key="index"
                  @click="selectFurnishing(locfur.label)"
                  class="px-4 py-2 cursor-pointer text-sm border-b border-gray-100 hover:bg-gray-100"
                  :class="{
                    'bg-gray-800 text-white font-semibold':
                      selectedFurnishing === locfur.label,
                  }"
                >
                  {{ locfur.label }}
                </li>
              </ul>
            </div>

            <!-- balcony template section -->
            <div class="relative inline-block text-left">
              <!-- Dropdown Trigger -->
              <button
                @click="isOpenBalcony = !isOpenBalcony"
                class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:border-olive transition-colors bg-white"
                :disabled="balconyLoading"
              >
                <span class="text-black font-bold text-[14px]">
                  {{
                    balconyLoading
                      ? "Loading…"
                      : balconyError
                      ? "Retry load"
                      : selectedBalconyLabel
                  }}
                </span>
                <NuxtImg
                  src="https://kots-world.b-cdn.net/Final/assets/images/arrow-circle-down.png"
                  alt="arrow circle down"
                  width="16"
                  height="16"
                  loading="lazy"
                  decoding="async"
                  class="img-dropdown-icon"
                  :class="[
                    isOpenBalcony ? 'img-rotate-180' : 'img-rotate-0',
                  ]"
                />
              </button>

              <!-- Optional error + retry -->
              <div v-if="balconyError" class="text-red-600 text-xs mt-1">
                {{ balconyError }}
                <button class="underline ml-1" @click="loadBalconies()">
                  Retry
                </button>
              </div>

              <!-- Dropdown List -->
              <ul
                v-if="isOpenBalcony"
                class="absolute mt-2 w-[9em] bg-white border border-gray-200 rounded-lg shadow-lg z-10"
              >
                <li
                  v-for="(locbal, index) in balcony"
                  :key="index"
                  @click="selectBalcony(locbal.label)"
                  class="px-4 py-2 cursor-pointer text-sm border-b border-gray-100 hover:bg-gray-100"
                  :class="{
                    'bg-gray-800 text-white font-semibold':
                      selectedBalcony === locbal.label,
                  }"
                >
                  {{ locbal.label }}
                </li>
              </ul>
            </div>
            <div class="relative inline-block text-left">
              <button
                @click="isOpenSortby = !isOpenSortby"
                class="bg-white flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:border-olive transition-colors"
              >
                <span class="text-black font-bold text-[14px]">{{
                  selectedSortby
                }}</span>
                <NuxtImg
                  src="https://kots-world.b-cdn.net/Final/assets/images/sort.png"
                  alt="sort"
                  width="16"
                  height="16"
                  loading="lazy"
                  decoding="async"
                  class="w-4 h-4"
                />
              </button>
              <ul
                v-if="isOpenSortby"
                class="absolute mt-2 w-[14em] bg-white border border-gray-200 rounded-lg shadow-lg z-10"
                :class="dropdownPosition"
              >
                <li
                  v-for="(option, index) in sortOptions"
                  :key="index"
                  @click="selectSortby(option)"
                  class="px-4 py-2 cursor-pointer text-sm hover:bg-gray-100 border-b last:border-b-0 border-gray-100"
                  :class="{
                    'bg-gray-800 text-white font-semibold':
                      selectedSortby === option,
                  }"
                >
                  {{ option }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        <!-- Loading State -->
        <div v-if="isLoadingFilteredFlats" class="flex justify-center items-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#afa11e]"></div>
          <span class="ml-2 text-gray-600">Loading flats...</span>
        </div>
        
        <!-- No Results Message -->
        <div v-else-if="displayedFlats.length === 0" class="text-center py-12">
          <p class="text-gray-600 text-lg">No flats found matching your filters.</p>
          <button
            @click="resetToDefaults"
            class="mt-4 text-[#afa11e] hover:underline font-medium"
          >
            Clear filters
          </button>
        </div>
        
        <!-- Flats Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8" :key="filterKey">
          <div
            v-for="flat in displayedFlats"
            :key="flat.code"
            :data-id="flat.id"
            :data-flattype="flat.type"
            :data-balcony="flat.balconyType"
            :data-furnish="flat.furnishData"
            class="bg-white rounded-xl shadow p-4 flex flex-col md:flex-row items-stretch md:items-center propertyFlats"
          >
            <!-- Desktop wrapper for link -->
            <a
              :href="flat.userFriendlyUrl"
              class="hidden md:flex md:items-center w-full"
              style="color: inherit; text-decoration: none"
            >
              <!-- Image (desktop) -->
              <div class="relative w-40 h-32 flex-shrink-0">
                <img
                  :src="flat.image"
                  :alt="metaTitleForAlt"
                  class="img-flat-image flatImg"
                  width="296"
                  height="192"
                  style="image-orientation: from-image;"
                  loading="lazy"
                  decoding="async"
                />
                <!-- Furnishing Badge -->
                <div class="absolute bottom-2 left-2">
                  <div
                    class="bg-black/80 text-white text-xs px-2 py-1 rounded flex items-center gap-1"
                  >
                    <NuxtImg
                      src="https://kots-world.b-cdn.net/Final/assets/images/monitor.png"
                      :alt="metaTitleForAlt"
                      width="12"
                      height="12"
                      loading="lazy"
                      decoding="async"
                      class="img-w3-h3"
                    />
                    {{ flat.furnished }}
                  </div>
                </div>
                <!-- Flat Type Badge -->
                <div class="absolute top-2 right-2">
                  <button
                    class="bg-white text-[#292d32] text-xs px-2 py-1 rounded border type-button"
                  >
                    {{ flat.type }}
                  </button>
                </div>
              </div>
              <!-- Content (desktop) -->
              <div class="flex-1 ml-6 flex flex-col justify-between h-full">
                  <!-- Availability -->
                  <div class="text-gray-500 available-tomorrow text-sm font-normal text-center border-y-2 border-[#f8f8f8] py-[10px] my-[10px] mb-[15px]">
                    {{ flat.availableFrom }}
                  </div>
                <!-- Flat info (desktop) -->
                <div class="flex flex-col gap-2 md:block">
                  <h3 class="text-lg text-[#292d32] res-title kota-res-size fw-bold">
                    {{ flat.code }}
                  </h3>
                  <div class="text-[#292d32] text-lg font-semibold res-price-sec">
                    <p class="res-price kot-res-price">
                      {{ flat.rent }}
                      <span class="text-sm font-normal">/mo.</span>
                    </p>
                  </div>
                </div>
              </div>
            </a>
            
            <!-- Mobile layout -->
            <div class="flex md:hidden flex-col w-full">
              <!-- Image link (mobile) -->
              <a
                :href="flat.userFriendlyUrl"
                class="block w-full"
                style="color: inherit; text-decoration: none"
              >
                <div class="relative w-full h-48">
                  <img
                    :src="flat.image"
                    :alt="metaTitleForAlt"
                    width="348"
                    height="192"
                    class="img-flat-image flatImg"
                    style="image-orientation: from-image;"
                    loading="lazy"
                    decoding="async"
                  />
                  <!-- Availability - Top Left on Mobile -->
                <div class="absolute top-2 left-2 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-md shadow-sm">
                  <div class="text-gray-700 text-xs font-medium">
                    {{ flat.availableFrom }}
                  </div>
                </div>
                  <!-- Furnishing Badge -->
                  <div class="absolute bottom-2 left-2">
                    <div
                      class="bg-black/80 text-white text-xs px-2 py-1 rounded flex items-center gap-1"
                    >
                      <img
                        src="https://kots-world.b-cdn.net/Final/assets/images/monitor.png"
                        :alt="metaTitleForAlt"
                        class="w-3 h-3"
                        width="12"
                        height="12"
                      />
                      {{ flat.furnished }}
                    </div>
                  </div>
                  <!-- Flat Type Badge -->
                  <div class="absolute top-2 right-2">
                    <button
                      class="bg-white text-[#292d32] text-xs px-2 py-1 rounded border type-button"
                    >
                      {{ flat.type }}
                    </button>
                  </div>
                </div>
              </a>
              
        
              
              <!-- Info row with button (mobile) -->
              <div class="flex items-center justify-between gap-4 mt-4">
                <a
                  :href="flat.userFriendlyUrl"
                  class="flex-1"
                  style="color: inherit; text-decoration: none"
                >
                  <div class="flex flex-col gap-1">
                    <h3 class="text-lg text-[#292d32] res-title kota-res-size fw-bold">
                      {{ flat.code }}
                    </h3>
                    <div class="text-[#292d32] text-[1.5em] sm:text-lg font-semibold res-price-sec">
                    <p class="res-price kot-res-price">
                      {{ flat.rent }}
                      <span class="text-sm font-normal">/mo.</span>
                    </p>
                </div>
              </div>
            </a>
                
                <!-- Action Button (mobile) -->
            <button
                  class="bg-[#f7f7e8] hover:bg-[#eaeacb] rounded-full w-10 h-10 flex items-center justify-center flex-shrink-0 res-card-img cursor-pointer"
                  @click="goToPayment(flat)"
                >
                  <NuxtImg
                    src="https://kots-world.b-cdn.net/Final/assets/images/res-arrow-right.png"
                    :alt="metaTitleForAlt"
                    width="24"
                    height="24"
                    loading="lazy"
                    decoding="async"
                    class="img-w6-h6"
                  />
                </button>
              </div>
            </div>
            
            <!-- Desktop Action Button -->
            <button
              class="hidden md:flex ml-4 bg-[#f7f7e8] hover:bg-[#eaeacb] rounded-full w-10 h-10 items-center justify-center res-card-img cursor-pointer"
              @click="goToPayment(flat)"
            >
              <img
                src="https://kots-world.b-cdn.net/Final/assets/images/res-arrow-right.png"
                :alt="metaTitleForAlt"
                class="img-w6-h6"
              />
            </button>
          </div>
        </div>
        
        <!-- View More Button -->
        <div v-if="hasMoreFlats" class="flex justify-center mt-8">
          <button
            @click="loadMoreFlats"
            :disabled="isLoadingMoreFlats"
            class="bg-[#afa11e] hover:bg-[#3d4247] text-white font-semibold px-8 py-3 rounded-lg transition-all duration-300 flex items-center gap-2 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="!isLoadingMoreFlats">View More</span>
            <span v-else>Loading...</span>
            <svg v-if="!isLoadingMoreFlats" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            <div v-else class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
          </button>
        </div>
      </div>
    </div>
    <!-- flats available section end -->
    <!-- blogs section start -->
    <div class="py-8 max-w-7xl mx-auto">
      <!-- Header -->
      <div
        class="flex justify-between items-start mb-8 px-4 md:flex-row flex-col gap-4 md:gap-0"
      >
        <div>
          <h3 class="text-2xl font-semibold text-gray-900 m-0">
            {{ carouselPropertyCount !== null && carouselPropertyCount !== undefined ? carouselPropertyCount : carouselProperties.length }} Apartments for Rent            near
            {{ property?.title || nearLocation }}
          </h3>
          <h3 class="text-xl font-normal text-gray-600 mt-1 m-0">
            {{ property?.area || location }}
          </h3>
        </div>

        <!-- Navigation arrows -->
        <div class="flex gap-2 md:self-auto self-end">
          <button
            class="w-10 h-10 border border-gray-300 rounded-full bg-white flex items-center justify-center cursor-pointer transition-all duration-200 hover:bg-gray-50 hover:border-gray-400 disabled:opacity-40 disabled:cursor-not-allowed"
            @click="scrollLeft"
            :disabled="!canScrollLeft"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path
                d="M15 18L9 12L15 6"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
          <button
            class="w-10 h-10 border border-gray-300 rounded-full bg-white flex items-center justify-center cursor-pointer transition-all duration-200 hover:bg-gray-50 hover:border-gray-400 disabled:opacity-40 disabled:cursor-not-allowed"
            @click="scrollRight"
            :disabled="!canScrollRight"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path
                d="M9 18L15 12L9 6"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Property Cards Container -->
      <div class="overflow-x-auto scrollbar-hide" ref="cardsContainer">
        <!-- Loading State -->
        <div v-if="carouselLoading" class="flex gap-6 px-4">
          <div
            v-for="n in 3"
            :key="n"
            class="min-w-[354px] bg-white rounded-[10px] shadow-[0_8px_15px_rgba(0,0,0,0.08)] overflow-hidden p-[15px] border border-[#f4f4f4] animate-pulse"
          >
            <div class="h-48 bg-gray-200 rounded-[25px] mb-4"></div>
            <div class="h-4 bg-gray-200 rounded mb-2"></div>
            <div class="h-6 bg-gray-200 rounded mb-2"></div>
            <div class="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </div>

        <!-- Properties Carousel -->
        <div v-else class="flex gap-6 px-4">
          <div
            v-for="(carouselProperty, index) in carouselProperties"
            :key="carouselProperty.id"
            class="min-w-80 bg-white rounded-xl overflow-hidden shadow-lg transition-all duration-300 ease-in-out cursor-pointer hover:-translate-y-1 hover:shadow-2xl bg-white rounded-[10px] shadow-[0_8px_15px_rgba(0,0,0,0.08)] overflow-hidden w-fit min-w-[354px] p-[15px] border border-[#f4f4f4] border border-[#f4f4f4] shadow-[0_8px_15px_rgba(0,0,0,0.08)] mt-[10px] mr-[40px] mb-[10px] ml-[5px]"
            @click="navigateToCarouselProperty(carouselProperty)"
          >
            <!-- Property Image -->
            <div class="relative h-48  overflow-hidden">
              <NuxtImg
                :src="getCarouselPropertyImage(carouselProperty)"
                :alt="metaTitleForAlt"
                class="w-full h-full object-cover h-auto block w-full rounded-[25px]"
                width="354"
                height="192"
                :loading="index === 0 ? 'eager' : 'lazy'"
                decoding="async"
              />

              <!-- Availability Badge (matching PHP logic) -->
              <div
                class="absolute top-3 left-3 px-[10px] py-2 rounded-lg text-sm flex items-center gap-2 text-white font-medium bg-black/65 bg-opacity-90"
              >
                <NuxtImg
                  src="https://kots-world.b-cdn.net/Final/assets/images/warning.png"
                  alt="warning"
                  width="16"
                  height="16"
                  loading="lazy"
                  decoding="async"
                  class="img-w4-h4"
                />
                <span>{{ carouselProperty.availabilityBadge.text }}</span>
              </div>

              <!-- Filling Fast Badge (if less than 10 flats) -->
              <div
                v-if="carouselProperty.availabilityBadge.showFillingFast"
                class="absolute top-14 left-3 px-[10px] py-2 rounded-lg text-sm flex items-center gap-2 text-white font-medium bg-black/65 bg-opacity-90"
              >
                <NuxtImg
                  src="https://kots-world.b-cdn.net/Final/assets/images/flash.png"
                  alt="flash"
                  width="16"
                  height="16"
                  loading="lazy"
                  decoding="async"
                  class="img-w4-h4"
                />
                <span>Filling fast</span>
              </div>
            </div>

            <!-- Property Details -->
            <div class="p-6">
              <!-- Property Types (matching PHP flat type ordering) -->
              <div class="flex flex-wrap gap-2 mb-4">
                <button
                  v-for="flatType in carouselProperty.formattedFlatTypes"
                  :key="flatType"
                  class="bg-[#f8f8f8] border-none rounded-[5px] px-[10px] py-[5px] cursor-pointer text-[12px] !text-black type-button"
                >
                  {{ flatType }}
                </button>
              </div>

              <!-- Property Name -->
              <h4 class="text-xl font-semibold text-gray-900 mb-2 res-title">
                {{ carouselProperty.name }}
              </h4>

              <!-- Location -->
              <p class="text-gray-600 text-sm mb-6 res-location">
                {{ carouselProperty.location }}
              </p>

              <!-- Price and CTA -->
              <div class="flex justify-between items-center res-price-sec">
                <div class="flex items-baseline gap-1">
                  <span class="text-gray-600 text-sm">From</span>
                  <span class="text-xl font-semibold text-gray-900 res-price"
                    >₹{{
                      carouselProperty.rentStartsFrom.toLocaleString("en-IN")
                    }}</span
                  >
                  <span class="text-gray-600 text-sm">/mo.</span>
                </div>

                <button
                  class="w-10 h-10 bg-[#f5f4e4] border-0 rounded-full text-white flex items-center justify-center cursor-pointer transition-all duration-200 hover:bg-yellow-600 hover:scale-105 res-card-img"
                  @click="goToProperty(carouselProperty)"
                >
                  <NuxtImg
                    src="https://kots-world.b-cdn.net/Final/assets/images/res-arrow-right.png"
                    :alt="metaTitleForAlt"
                    width="24"
                    height="24"
                    loading="lazy"
                    decoding="async"
                    class="img-w6-h6"
                  />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- blogs section end -->

    <!-- features at kots start -->
    <ClientOnly>
      <Suspense>
        <template #default>
          <FeaturesAtKotsV2 />
        </template>
        <template #fallback>
          <div class="min-h-[400px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>

    <ClientOnly>
      <Suspense>
        <template #default>
          <TenantReviews />
        </template>
        <template #fallback>
          <div class="min-h-[300px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>

    <ClientOnly>
      <Suspense>
        <template #default>
          <MediaSpotlight />
        </template>
        <template #fallback>
          <div class="min-h-[300px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>

    <ClientOnly>
      <Suspense>
        <template #default>
          <Faqs heading-level="h2"/>
        </template>
        <template #fallback>
          <div class="min-h-[300px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>

    <ClientOnly>
      <Suspense>
        <template #default>
          <KotsProjectsContactUs id="contact-section" />
        </template>
        <template #fallback>
          <div class="min-h-[300px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>

    <ClientOnly>
      <Suspense>
        <template #default>
          <Footer />
        </template>
        <template #fallback>
          <div class="min-h-[300px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>
    
    <!-- Mobile Footer - Fixed at bottom for mobile only -->
    <ClientOnly>
      <Suspense>
        <template #default>
          <MobileFooter :filterKey="filterKey" />
        </template>
        <template #fallback>
          <div class="min-h-[100px] bg-white flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </template>
      </Suspense>
    </ClientOnly>
    <!-- features at kots end -->
    </div>

  <div v-if="!isCategoryPage && !property && !propertyLoading">
    <p class="text-red-600 text-xl">Property not found.</p>
  </div>

  <!-- Mobile Sticky Bottom Property Card -->
  <div class="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50 transition-all duration-300 min-h-[107px]" v-if="!isCategoryPage">
    <div class="p-4">
      <!-- Collapsed View (Always Visible) -->
      <div class="flex items-center justify-between">
        <!-- Basic Property Info -->
        <div class="flex-1">
          <div v-if="showMobileDetails">
            <h3 class="font-bold text-lg leading-tight">
              {{ property?.title || "KOTS ABODE" }}
            </h3>
            <p class="text-sm text-gray-600">
            <span v-if="availableFlatTypes.length > 0">
            {{ availableFlatTypes.join(', ') }}
            </span>
            <span v-else>{{ property?.type || "1 BHK - 2 BHK" }}</span>
            </p>
            <p class="text-sm text-gray-600">
              {{ property?.location || property?.localityDescription || property?.area || "Whitefield" }}
            </p>
          </div>
          <p class="font-bold text-sm mt-1">Rent Starts From</p>
          <p class="font-bold text-lg mt-1">
             {{ property?.rent || "₹ 32,800/mo." }}
          </p>
        </div>
        
        <!-- Toggle Button -->
        <div class="view-detail view-more cursor-pointer flex flex-col items-center" @click="toggleMobileDetails">
          <NuxtImg 
            src="https://kots-world.b-cdn.net/Final/assets/images/arrow-circle-down.png" 
            alt="Toggle Details"
            loading="lazy"
            decoding="async"
            class="transition-transform duration-300"
            :style="{ transform: showMobileDetails ? 'rotate(0deg)' : 'rotate(180deg)' }"
            width="20"
            height="20"
          />
          <span class="view-sec">{{ showMobileDetails ? 'Hide Details' : 'View Details' }}</span>
        </div>
      </div>

      <!-- Expanded Details (Conditional) -->


      <!-- CTA Button (Always Visible) -->
      <div class="mt-4">
        <button
          class="bg-[#afa11e] hover:bg-[#afa11e]/80 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex justify-center items-center whitespace-nowrap w-full"
          @click="scrollToFlats"
        >
          Show {{ totalAvailableFlats !== null && totalAvailableFlats !== undefined ? totalAvailableFlats : (property?.flats?.length || 0) }} flats
          <svg
            class="w-4 h-4 ml-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
  
  <script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, watch, defineAsyncComponent } from "vue";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";
import { resolveFriendlyUrl } from "~/services/urlResolverService";
import { amenitiesService } from "~/services/amenitiesService";
import { propertiesService } from "~/services/propertiesService";
import { usePropertyContext } from "~/composables/usePropertyContext";
import { useNearbyPlaces } from "~/composables/useNearbyPlaces";
import Datepicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

// Define all components as async for code splitting
const HomePageCarousel = defineAsyncComponent(() => import('~/components/HomePageCarousel.vue'));
const FeaturesAtKotsLanding = defineAsyncComponent(() => import('~/components/FeaturesAtKotsLanding.vue'));
const FlatsAvailableSection = defineAsyncComponent(() => import('~/components/FlatsAvailableSection.vue'));
const PropertiesCarousel = defineAsyncComponent(() => import('~/components/PropertiesCarousel.vue'));
const TenantReviews = defineAsyncComponent(() => import('~/components/TenantReviews.vue'));
const MediaSpotlight = defineAsyncComponent(() => import('~/components/MediaSpotlight.vue'));
const KotsProjectsFaq = defineAsyncComponent(() => import('~/components/KotsProjectsFaq.vue'));
const KotsProjectsContactUs = defineAsyncComponent(() => import('~/components/KotsProjectsContactUs.vue'));
const Footer = defineAsyncComponent(() => import('~/components/Footer.vue'));
const MobileFooter = defineAsyncComponent(() => import('~/components/MobileFooter.vue'));
const FeaturesAtKotsV2 = defineAsyncComponent(() => import('~/components/FeaturesAtKotsV2.vue'));
const Faqs = defineAsyncComponent(() => import('~/components/Faqs.vue'));

const router = useRouter();

// Make property reactive - moved to top
const property = ref(null);
// propertyLoading is now from useAsyncData below

// Computed property to check if property section should be shown
const showPropertySection = computed(() => {
  return property.value && !isCategoryPage.value;
});

// Store availableFlats count from API
const totalAvailableFlats = ref(null);

// Reactive data for nearby places (declared early for SSR initialization)
const nearbyPlaces = ref([]);
const nearbyPlacesLoading = ref(false);

// Pagination offset for loading more flats
const flatsOffset = ref(5); // Start at 5 since initial load is 6
const isLoadingMoreFlats = ref(false);

// Guard to prevent access before initialization
const componentReady = ref(false);

// Filter-related refs - must be declared before use in computed properties and functions
const isOpenLocality = ref(false);
const selected = ref("Flat Type");
const isOpenFurnishing = ref(false);
const selectedFurnishing = ref("Furnishing");
const isOpenBalcony = ref(false);
const selectedBalcony = ref("Balcony");
const showMobileDetails = ref(false);
const balconyLoading = ref(false);
const balconyError = ref(null);
const isOpenSortby = ref(false);
const selectedSortby = ref("Sort By");
const today = new Date();
const selectedDate = ref(
  today.toISOString().slice(0, 10) // "YYYY-MM-DD"
);
const dateFilterActive = ref(false); // Track if user has selected a date
const isOpenDatePicker = ref(false);

// Category page handling
const isCategoryPage = ref(false);
const categoryType = ref('');
const categoryValue = ref('');

// Dynamic category name that updates based on filters
const { useUiStore } = await import('~/stores/ui');
const ui = useUiStore();

// Fix the dynamicCategoryName computed property
const dynamicCategoryName = computed(() => {
  // Check if there's an active flat type filter
  const activeFilters = ui.searchFilters;
  
  if (activeFilters.flatType && activeFilters.flatType.trim() !== '') {
    return activeFilters.flatType;
  }
  
  // Fall back to the original category from URL (use propertySlug instead of category)
  const categoryInfo = parseCategory(propertySlug);
  return categoryInfo ? categoryInfo.value : slugToTitle(propertySlug);
});

// Add dynamic area name computed property
const dynamicAreaName = computed(() => {
  // Check if there's an active location filter
  const activeFilters = ui.searchFilters;
  
  let areaName = '';
  if (activeFilters.location && activeFilters.location.trim() !== '') {
    areaName = activeFilters.location;
  } else {
    // Fall back to the original area from URL
    areaName = slugToTitle(area);
  }
  
  // Handle specific case for HSR
  if (areaName.toLowerCase() === 'hsr') {
    return 'HSR';
  }
  
  return areaName;
});

// Helper function to map furnishing type codes to string values
const getFurnishingTypeName = (furnishingTypeCode) => {
  switch (furnishingTypeCode) {
    case 1: return 'Fully Furnished';
    case 2: return 'Fully Furnished AC';
    case 3: return 'Semi-Furnished';
    default: return '';
  }
};

// Helper function to get availability text from flat data
const getAvailabilityTextFromFlat = (flat) => {
  const flatAvailableStatus = flat.flat_available_status;
  const availableDateforNextBooking = flat.available_date_for_next_booking;

  if (flatAvailableStatus === null || flatAvailableStatus === undefined) {
    return "Flat not Available";
  }

  const isStatusAvailable = [1, 3].includes(flatAvailableStatus);

  if (!isStatusAvailable) {
    return "Flat not Available";
  }

  if (
    isStatusAvailable &&
    availableDateforNextBooking &&
    availableDateforNextBooking !== "0000-00-00" &&
    availableDateforNextBooking !== null
  ) {
    const availableDate = new Date(availableDateforNextBooking);
    const today = new Date();

    today.setHours(0, 0, 0, 0);
    availableDate.setHours(0, 0, 0, 0);

    if (availableDate > today) {
      return `Available from ${availableDate.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      })}`;
    }
  }

  return "Available from Tomorrow";
};

// Helper function to convert GMT date string to mm/dd/yyyy format
const convertGMTToMMDDYYYY = (gmtDateString) => {
  if (!gmtDateString) return '';
  
  try {
    const date = new Date(gmtDateString);
    if (isNaN(date.getTime())) return '';
    
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const year = date.getFullYear();
    
    return `${month}/${day}/${year}`;
  } catch (error) {
    return '';
  }
};

// ✅ SSR: Fetch flats data on server-side for FlatsAvailableSection
// Note: route params will be accessed via useRoute() inside the async function
const routeForFlats = useRoute();
const { data: flatsData } = await useAsyncData(
  `flats-for-section-${routeForFlats.params.city}-${routeForFlats.params.area}-${routeForFlats.params.property}`,
  async () => {
    try {
      // Get area parameter - use locationSlug from store if available and not "bangalore", otherwise use route area
      const locationSlug = ui.searchFilters.locationSlug;
      const areaToUse = (locationSlug && locationSlug.toLowerCase() !== 'bangalore') 
        ? locationSlug 
        : routeForFlats.params.area;

      // Get filter parameters from UI store
      let flatTypeToUse = undefined;
      let balconyTypeToUse = undefined;
      let furnishTypeToUse = undefined;
      let availableDateToUse = undefined;
      let sortByToUse = undefined;

      // Get flat type from search filters
      if (ui.searchFilters.flatType && ui.searchFilters.flatType !== 'Flat Type') {
        flatTypeToUse = ui.searchFilters.flatType;
      }

      // Get furnish type code from furnishing filter
      const getFurnishTypeCode = (furnishing) => {
        if (!furnishing || furnishing === 'Furnishing') return undefined;
        const normalized = furnishing.toLowerCase().trim();
        if (normalized.includes('fully furnished ac') || normalized === 'fully furnished ac') {
          return '2';
        } else if (normalized.includes('fully furnished') || normalized === 'fully furnished') {
          return '1';
        } else if (normalized.includes('semi') || normalized === 'semi-furnished') {
          return '3';
        }
        return undefined;
      };
      
      if (ui.searchFilters.furnishing) {
        furnishTypeToUse = getFurnishTypeCode(ui.searchFilters.furnishing);
      }
      
      // Get balcony type from balcony filter
      if (ui.searchFilters.balcony && ui.searchFilters.balcony !== '' && ui.searchFilters.balcony !== 'Balcony') {
        balconyTypeToUse = ui.searchFilters.balcony;
      }
      
      // Get available date from moveInDate filter
      if (ui.searchFilters.moveInDate) {
        try {
          const date = new Date(ui.searchFilters.moveInDate);
          if (!isNaN(date.getTime())) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            availableDateToUse = `${year}-${month}-${day}`;
          }
        } catch (e) {
          // If date parsing fails, skip
        }
      }
      
      // Get sortBy from search filters
      if (ui.searchFilters.sortBy && ui.searchFilters.sortBy !== '' && ui.searchFilters.sortBy !== 'Sort By') {
        sortByToUse = ui.searchFilters.sortBy;
      }

      const response = await propertiesService.getFormattedPropertiesForResults(
        areaToUse, 
        10, // Limit to 10 properties
        flatTypeToUse,
        balconyTypeToUse,
        furnishTypeToUse,
        availableDateToUse,
        sortByToUse
      );

      // Extract all flats from properties
      const allFlats = [];
      if (response.properties && Array.isArray(response.properties)) {
        response.properties.forEach(property => {
          if (property.flats && Array.isArray(property.flats)) {
            property.flats.forEach(flat => {
              allFlats.push({
                id: flat.id,
                code: flat.name || `${property.title} - ${flat.flatType || 'Flat'}`,
                type: flat.flatType || 'Studio',
                image: `https://kots-world.b-cdn.net/Final/productImages/Finall/${flat?.flat_featured_image?.savedName}` || property.image,
                furnished: getFurnishingTypeName(flat.furnishing_type) || flat.furnished || 'Fully Furnished',
                furnishData: flat.furnishing_type ? (flat.furnishing_type === 1 ? 'fully-furnished' : flat.furnishing_type === 2 ? 'fully-furnished-ac' : 'semi-furnished') : 'fully-furnished',
                balconyType: flat.balconyType || flat.balcony_type || 'With Balcony',
                balcony_type_id: flat.balcony_type_id || flat.flat_balcony_id,
                flat_balcony_id: flat.flat_balcony_id,
                furnishing_type: flat.furnishing_type,
                availableFrom: getAvailabilityTextFromFlat(flat),
                availableFromMMDDYYYY: convertGMTToMMDDYYYY(flat.available_date_for_next_booking),
                rent: flat.selling_price || `₹${property.rent?.replace(/[₹,]/g, '') || '25,000'}`,
                userFriendlyUrl: flat.user_friendly_url || property.user_friendly_url,
                propertyName: property.title,
                propertyLocation: property.sub_title || property.place,
                place: property.sub_title || property.place
              });
            });
          }
        });
      }

      return {
        flats: allFlats,
        totalFlatCount: response.totalFlatCount || null
      };
    } catch (error) {
      console.error("Error loading flats for FlatsAvailableSection:", error);
      return {
        flats: [],
        totalFlatCount: null
      };
    }
  },
  {
    server: true,      // ✅ SSR: Fetch on server
    lazy: true,        // Non-blocking: Don't delay initial render
    default: () => ({ flats: [], totalFlatCount: null })
  }
);

// ✅ SSR: Fetch properties data on server-side for PropertiesCarousel
// Use route params in the key to make it reactive to route changes
const routeForCarousel = useRoute();
const { data: propertiesCarouselData, refresh: refreshCarouselData } = await useAsyncData(
  () => `properties-carousel-${routeForCarousel.params.city}-${routeForCarousel.params.area}-${routeForCarousel.params.property}`,
  async () => {
    try {
      // Get area parameter - use locationSlug from store if available and not "bangalore", otherwise use route area
      const locationSlug = ui.searchFilters.locationSlug;
      const areaToUse = (locationSlug && locationSlug.toLowerCase() !== 'bangalore') 
        ? locationSlug 
        : routeForCarousel.params.area;

      // Get filter parameters from UI store (same logic as PropertiesCarousel)
      let flatTypeToUse = undefined;
      let balconyTypeToUse = undefined;
      let furnishTypeToUse = undefined;
      let availableDateToUse = undefined;
      let sortByToUse = undefined;

      // Get flat type from search filters
      if (ui.searchFilters.flatType && ui.searchFilters.flatType !== 'Flat Type') {
        flatTypeToUse = ui.searchFilters.flatType.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
      }

      // Get furnish type code from furnishing filter
      const getFurnishTypeCode = (furnishing) => {
        if (!furnishing) return undefined;
        const normalized = furnishing.toLowerCase().trim();
        if (normalized === 'all' || normalized === '') {
          return undefined;
        }
        if (normalized.includes('fully furnished ac') || normalized === 'fully furnished ac') {
          return '2';
        } else if (normalized.includes('fully furnished') || normalized === 'fully furnished') {
          return '1';
        } else if (normalized.includes('semi') || normalized === 'semi-furnished') {
          return '3';
        }
        return undefined;
      };
      
      if (ui.searchFilters.furnishing) {
        furnishTypeToUse = getFurnishTypeCode(ui.searchFilters.furnishing);
      }
      
      // Get balcony type from balcony filter
      if (ui.searchFilters.balcony && ui.searchFilters.balcony !== '' && ui.searchFilters.balcony !== 'All') {
        balconyTypeToUse = ui.searchFilters.balcony;
      }
      
      // Get available date from moveInDate filter
      if (ui.searchFilters.moveInDate) {
        try {
          const date = new Date(ui.searchFilters.moveInDate);
          if (!isNaN(date.getTime())) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            availableDateToUse = `${year}-${month}-${day}`;
          }
        } catch (e) {
          // If date parsing fails, skip
        }
      }
      
      // Get sortBy from search filters
      if (ui.searchFilters.sortBy && ui.searchFilters.sortBy !== '' && ui.searchFilters.sortBy !== 'Sort By') {
        sortByToUse = ui.searchFilters.sortBy;
      }

      const response = await propertiesService.getFormattedPropertiesForResults(
        areaToUse, 
        10, // Limit to 10 properties (matching the limit prop)
        flatTypeToUse,
        balconyTypeToUse,
        furnishTypeToUse,
        availableDateToUse,
        sortByToUse
      );

      return {
        properties: response.properties || [],
        propertyCount: response.propertyCount ?? null,
        totalFlatCount: response.totalFlatCount ?? null
      };
    } catch (error) {
      console.error("Error loading carousel properties:", error);
      return {
        properties: [],
        propertyCount: null,
        totalFlatCount: null
      };
    }
  },
  {
    server: true,      // ✅ SSR: Fetch on server
    lazy: true,        // Non-blocking: Don't delay initial render
    watch: [() => routeForCarousel.params.area, () => routeForCarousel.params.city, () => routeForCarousel.params.property], // ✅ Watch route params for changes
    default: () => ({ properties: [], propertyCount: null, totalFlatCount: null })
  }
);

// ✅ Watch for route changes and refresh carousel data
watch(() => routeForCarousel.params.area, async (newArea, oldArea) => {
  if (newArea !== oldArea && process.client) {
    await refreshCarouselData();
  }
});

// Track if filters have been applied (client-side)
const filtersApplied = ref(false);

// Keep refs for client-side filter updates
const flatsRef = ref([]);
const totalFlatCountRef = ref(null);

// Reactive data for category page (from SSR, but can be updated client-side)
const flats = computed(() => {
  // If filters have been applied client-side, always use refs (even if empty)
  // This ensures filtered results (including empty results) are shown
  if (filtersApplied.value) {
    return flatsRef.value;
  }
  // Use SSR data if available, otherwise fallback to ref
  if (flatsData.value && flatsData.value.flats !== undefined) {
    return flatsData.value.flats;
  }
  return flatsRef.value;
});

const totalFlatCountFromCarousel = computed(() => {
  // If filters have been applied client-side, always use ref (even if null)
  // This ensures filtered results are shown
  if (filtersApplied.value) {
    return totalFlatCountRef.value;
  }
  // Use SSR data if available, otherwise fallback to ref
  if (flatsData.value && flatsData.value.totalFlatCount !== undefined) {
    return flatsData.value.totalFlatCount;
  }
  return totalFlatCountRef.value;
});

// Helper function to map furnishing name to furnish_type code
const getFurnishTypeCode = (furnishingName) => {
  if (!furnishingName) return undefined;
  const normalized = furnishingName.toLowerCase().trim();
  // Only send if not "All" or empty
  if (normalized === 'all' || normalized === '') {
    return undefined;
  }
  if (normalized.includes('fully furnished ac') || normalized === 'fully furnished ac') {
    return '2';
  } else if (normalized.includes('fully furnished') || normalized === 'fully furnished') {
    return '1';
  } else if (normalized.includes('semi') || normalized === 'semi-furnished') {
    return '3';
  }
  return undefined;
};

// Handler for when filters change in FlatsAvailableSection - refetch data from API
const handleFiltersChanged = async (filters) => {
  console.log('[handleFiltersChanged] Filters changed:', filters);
  console.log('[handleFiltersChanged] Current store filters:', ui.searchFilters);
  
  try {
    const { propertiesService } = await import('~/services/propertiesService');
    
    // ✅ ALWAYS get all current filters from store, not just what's in the filters parameter
    // This ensures when sortBy changes, all other filters are still sent
    
    // ✅ Extract flat type - from filters or from store
    let flatTypeValue = filters.flatType || ui.searchFilters.flatType;
    
    if (flatTypeValue) {
      // Normalize flat type format (e.g., "2 BHK" or "2-BHK" -> "2 BHK")
      flatTypeValue = flatTypeValue.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
    }
    
    // ✅ Get balcony type - from filters or from store
    let balconyType = filters.balconyType;
    if (!balconyType && ui.searchFilters.balcony && ui.searchFilters.balcony !== '' && ui.searchFilters.balcony !== 'All') {
      balconyType = ui.searchFilters.balcony;
    }
    
    // ✅ Get furnish type - from filters or from store
    let furnishType = filters.furnish_type;
    if (!furnishType && ui.searchFilters.furnishing) {
      furnishType = getFurnishTypeCode(ui.searchFilters.furnishing);
    }
    
    // ✅ Get available date - from filters or from store
    let availableDate = filters.available_date_for_next_booking;
    if (!availableDate && ui.searchFilters.moveInDate) {
      try {
        const date = new Date(ui.searchFilters.moveInDate);
        if (!isNaN(date.getTime())) {
          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');
          availableDate = `${year}-${month}-${day}`;
        }
      } catch (e) {
        // If date parsing fails, skip
      }
    }
    
    // ✅ Ensure flatType is always sent (even if empty string)
    const flatTypeToSend = flatTypeValue || '';
    
    // ✅ Get sortBy - from filters or from store
    let sortByValue = filters.sortBy || ui.searchFilters.sortBy;
    // Only send if it's a valid sort option (not empty or "Sort By")
    if (sortByValue === '' || sortByValue === 'Sort By') {
      sortByValue = undefined;
    }
    
    // ✅ Get area parameter - use locationSlug from store if available and not "bangalore"
    // Otherwise use route area
    const routeForFilters = useRoute();
    let areaToUse = routeForFilters.params.area;
    const locationSlug = ui.searchFilters.locationSlug;
    if (locationSlug && locationSlug.toLowerCase() !== 'bangalore') {
      areaToUse = locationSlug;
    }
    
    console.log('[handleFiltersChanged] Calling API with params:', {
      areaToUse,
      limit: 26,
      flatTypeToSend,
      balconyType,
      furnishType,
      availableDate,
      sortByValue
    });
    
    // Call API with all filter parameters from store
    const response = await propertiesService.getFormattedPropertiesForResults(
      areaToUse,
      26, // Increase limit when filtering to get more results
      flatTypeToSend,
      balconyType,
      furnishType,
      availableDate,
      sortByValue
    );
    
    console.log('[handleFiltersChanged] API response received:', {
      propertiesCount: response?.properties?.length || 0,
      totalFlatCount: response?.totalFlatCount
    });
    
    if (response?.properties) {
      // Extract all flats from properties (API should already filter them)
      const allFlats = [];
      response.properties.forEach(property => {
        if (property.flats && Array.isArray(property.flats)) {
          property.flats.forEach(flat => {
            allFlats.push({
              id: flat.id,
              code: flat.name || `${property.title} - ${flat.flatType || 'Flat'}`,
              type: flat.flatType || 'Studio',
              image: `https://kots-world.b-cdn.net/Final/productImages/Finall/${flat?.flat_featured_image?.savedName}` || property.image,
              furnished: getFurnishingTypeName(flat.furnishing_type) || flat.furnished || 'Fully Furnished',
              furnishData: flat.furnishing_type ? (flat.furnishing_type === 1 ? 'fully-furnished' : flat.furnishing_type === 2 ? 'fully-furnished-ac' : 'semi-furnished') : 'fully-furnished',
              balconyType: flat.balconyType || flat.balcony_type || 'With Balcony',
              balcony_type_id: flat.balcony_type_id || flat.flat_balcony_id,
              flat_balcony_id: flat.flat_balcony_id,
              furnishing_type: flat.furnishing_type,
              availableFrom: getAvailabilityTextFromFlat(flat),
              availableFromMMDDYYYY: convertGMTToMMDDYYYY(flat.available_date_for_next_booking),
              rent: flat.selling_price || `₹${property.rent?.replace(/[₹,]/g, '') || '25,000'}`,
              userFriendlyUrl: flat.user_friendly_url || property.user_friendly_url,
              propertyName: property.title,
              propertyLocation: property.sub_title || property.place,
              place: property.sub_title || property.place
            });
          });
        }
      });
      
      // Mark that filters have been applied
      filtersApplied.value = true;
      
      // Update flats data (client-side updates)
      flatsRef.value = allFlats;
      
      // ✅ Update totalFlatCount from API response (for FlatsAvailableSection)
      if (response.totalFlatCount !== null && response.totalFlatCount !== undefined) {
        totalFlatCountRef.value = response.totalFlatCount;
        console.log(`[handleFiltersChanged] Updated totalFlatCount: ${response.totalFlatCount} for area: ${areaToUse}`);
      }
      
      // ✅ Also update PropertiesCarousel with filtered data
      // Fetch properties with the same filters for the carousel
      try {
        const carouselResponse = await propertiesService.getFormattedPropertiesForResults(
          areaToUse,
          10, // Limit to 10 properties
          flatTypeToSend,
          balconyType,
          furnishType,
          availableDate,
          sortByValue
        );
        
        // Update carousel data
        if (propertiesCarouselData.value) {
          propertiesCarouselData.value.properties = carouselResponse.properties || [];
          propertiesCarouselData.value.propertyCount = carouselResponse.propertyCount ?? null;
          propertiesCarouselData.value.totalFlatCount = carouselResponse.totalFlatCount ?? null;
        }
      } catch (error) {
        console.error('Failed to update carousel properties:', error);
      }
    }
  } catch (error) {
    console.error('Failed to fetch filtered flats:', error);
  }
};

// Handler for when flats are loaded from PropertiesCarousel (for client-side updates)
const handleFlatsLoaded = (loadedFlats) => {
  // Update flats if PropertiesCarousel provides new data (client-side only)
  if (process.client && loadedFlats && Array.isArray(loadedFlats)) {
    // Note: This will be handled by PropertiesCarousel component itself
    // We keep this for backward compatibility but flats are now SSR'd
  }
};

// Handler for when metadata (totalFlatCount) is loaded from PropertiesCarousel (for client-side updates)
const handleMetadataLoaded = (metadata) => {
  // Update totalFlatCount if PropertiesCarousel provides new data (client-side only)
  if (process.client && metadata.totalFlatCount !== null && metadata.totalFlatCount !== undefined) {
    // Note: This will be handled by PropertiesCarousel component itself
    // We keep this for backward compatibility but totalFlatCount is now SSR'd
  }
};

// ✅ Watch for filter changes in store and trigger API call
// This ensures API is called even if filtersChanged event is not emitted
watch(
  () => [
    ui.searchFilters.flatType,
    ui.searchFilters.furnishing,
    ui.searchFilters.balcony,
    ui.searchFilters.moveInDate,
    ui.searchFilters.sortBy
  ],
  async (newFilters, oldFilters) => {
    // Only trigger on client-side and if filters actually changed
    if (!process.client) return;
    
    // Check if any filter actually changed (not just reference)
    const hasChanged = newFilters.some((val, idx) => val !== oldFilters?.[idx]);
    
    if (hasChanged) {
      console.log('[Filter Watcher] Filters changed in store, triggering API call');
      // Call handleFiltersChanged with current store filters
      await handleFiltersChanged({});
    }
  },
  { deep: true }
)

// Helper functions for category detection
const slugToTitle = (slug) => {
  return slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const toTitleCase = (str) => {
  if (!str) return '';
  return str
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};
// Helper function to format property title to title case
const formatPropertyTitle = (title) => {
  if (!title) return '';
  // Convert to title case: first letter of each word capitalized, rest lowercase
  return title.toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
}

// Helper function to normalize flat type slugs to the correct format
const normalizeFlatTypeSlug = (slug) => {
  const slugLower = slug.toLowerCase()
  
  // Handle formats like '2bhk', '2-bhk', '1bhk', '1-bhk', etc.
  // Convert to '2 BHK', '1 BHK', etc.
  const bhkMatch = slugLower.match(/^(\d+(?:\.\d+)?)(-?)(bhk)$/)
  if (bhkMatch) {
    return `${bhkMatch[1]} BHK`
  }
  
  // Handle studio
  if (slugLower === 'studio') {
    return 'Studio'
  }
  
  // Fallback to slugToTitle for other formats
  return slugToTitle(slug)
}

const parseCategory = (slug) => {
  const slugLower = slug.toLowerCase()
  
  // Define category types
  const FLAT_TYPES = new Set([
    'studio', '1-bhk', '2-bhk', '2.5-bhk', '3-bhk', '4-bhk',
    '1bhk', '2bhk', '2.5bhk', '3bhk', '4bhk'
  ])
  
  const FURNISHING_TYPES = new Set([
    'semi-furnished', 'fully-furnished-ac', 'fully-furnished', 'unfurnished'
  ])
  
  const BALCONY_TYPES = new Set([
    'no-balcony', 'with-balcony'
  ])
  
  const PARKING_TYPES = new Set([
    'without-car-parking', 'with-car-parking'
  ])
  
  if (FLAT_TYPES.has(slugLower)) {
    return { type: 'flatType', value: normalizeFlatTypeSlug(slug) }
  } else if (FURNISHING_TYPES.has(slugLower)) {
    return { type: 'furnishing', value: slugToTitle(slug) }
  } else if (BALCONY_TYPES.has(slugLower)) {
    return { type: 'balcony', value: slugToTitle(slug) }
  } else if (PARKING_TYPES.has(slugLower)) {
    return { type: 'parking', value: slugToTitle(slug) }
  }
  
  return null
}

// Function to set SEO for category pages
const setCategorySEO = (categoryInfo, area, city) => {
  const areaName = slugToTitle(area);
  const cityName = slugToTitle(city);
  const categoryName = categoryInfo.value;
  
  const getMetaTitle = () => {
    if (categoryInfo.type === 'flatType') {
      return `${categoryName} Flats for Rent in ${areaName}, ${cityName} | Kots`;
    } else if (categoryInfo.type === 'furnishing') {
      return `${categoryName} Flats in ${areaName}, ${cityName} | Kots`;
    } else if (categoryInfo.type === 'balcony') {
      return `Flats ${categoryName} in ${areaName}, ${cityName} | Kots`;
    } else if (categoryInfo.type === 'parking') {
      return `Flats ${categoryName} in ${areaName}, ${cityName} | Kots`;
    }
    return `Properties in ${areaName} | Kots`;
  };
  
  const getMetaDescription = () => {
    if (categoryInfo.type === 'flatType') {
      return `Find ${categoryName.toLowerCase()} flats for rent in ${areaName}, ${cityName} with 24/7 power & water backup, high-speed internet, and tech-enabled security. Book your home now!`;
    } else if (categoryInfo.type === 'furnishing') {
      return `Discover ${categoryName.toLowerCase()} apartments in ${areaName}, ${cityName} with premium amenities and modern facilities. Experience comfortable living with Kots!`;
    } else {
      return `Explore flats in ${areaName}, ${cityName} with ${categoryName.toLowerCase()}. Premium managed apartments with world-class amenities and 24/7 services.`;
    }
  };
  
  const canonicalUrl = `/${city}/${area}/${propertySlug}`;
  
  useHead({
    title: getMetaTitle(),
    meta: [
      {
        name: 'description',
        content: getMetaDescription()
      },
      {
        name: 'keywords',
        content: `${categoryName} flats ${areaName}, apartments ${areaName}, rental homes ${areaName}, ${categoryName} properties ${cityName}, premium flats ${cityName}`
      }
    ],
    link: [
      {
        rel: 'canonical',
        href: `https://www.kots.world${canonicalUrl}`
      }
    ]
  });
}

// Get route parameters
const route = useRoute();
const area = route.params.area;
const city = route.params.city;
const propertySlug = route.params.property;

// ===== CAMPAIGN TRACKING =====
const { campaignId, hasCampaignData, trackPropertyDetailVisit } = useCampaignTracking()

// ALL COMPUTED PROPERTIES - MOVED TO TOP TO AVOID INITIALIZATION ERRORS

// Computed property for all flats from API data (unfiltered)
// ✅ SSR: Removed componentReady check to allow SSR rendering
const allFlats = computed(() => {
  if (!property.value?.flats) return [];

  return property.value.flats.map((flat, index) => {
    // Construct userFriendlyUrl from current route + flat slug
    let userFriendlyUrl = '';
    
    // Edge case 1: Check if all route parameters exist
    if (city && area && propertySlug && flat.flat_slug) {
      userFriendlyUrl = `/${city}/${area}/${propertySlug}/${flat.flat_slug}`;
    } 
    // Edge case 2: If flat_slug is missing, fallback to property page
    else if (city && area && propertySlug) {
      userFriendlyUrl = `/${city}/${area}/${propertySlug}`;
    } 
    // Edge case 3: If route params are missing, fallback to home
    else {
      userFriendlyUrl = '/';
    }

    return {
      id: index + 1,
      code: flat.flat_name,
      image: `https://kots-world.b-cdn.net/Final/productImages/Finall/${flat?.flat_featured_image?.savedName}`,
      furnished: getFurnishTypeLabel(flat.furnishing_type),
      furnishData: getFurnishTypeData(flat.furnishing_type),
      type: flat.flat_type,
      availableFrom: getAvailabilityText(flat),
      rent: `₹${parseFloat(
        flat.flat_selling_price || flat.selling_price
      ).toLocaleString("en-IN")}`,
      flatId: flat.flat_id,
      slug: flat.flat_slug,
      userFriendlyUrl: userFriendlyUrl,
      balconyType: flat.balcony_type,
      balconyId: flat.balcony_id,
      availableStatus: flat.flat_available_status,
      availableDate: flat.available_date_for_next_booking,
      available_date_for_next_booking: flat.available_date_for_next_booking, // Keep raw field for getAvailabilityDate
    };
  });
});

// Helper functions need to be declared before computed properties that use them
const getFurnishTypeLabel = (furnishingType) => {
  switch (furnishingType) {
    case 1: return "Fully Furnished";
    case 2: return "Fully Furnished AC";
    case 3: return "Semi-Furnished";
    // case 4: return "Unfurnished";
    default: return "";
  }
};

const getFurnishTypeData = (furnishingType) => {
  switch (furnishingType) {
    case 1: return "fully-furnished";
    case 2: return "fully-furnished-ac";
    case 3: return "semi-furnished";
    case 4: return "un-furnished";
    default: return "";
  }
};

const getAvailabilityText = (flat) => {
  const flatAvailableStatus = flat.flat_available_status;
  const availableDateforNextBooking = flat.available_date_for_next_booking;

  if (flatAvailableStatus === null || flatAvailableStatus === undefined) {
    return "Flat not Available";
  }

  const isStatusAvailable = [1, 3].includes(flatAvailableStatus);

  if (!isStatusAvailable) {
    return "Flat not Available";
  }

  if (
    isStatusAvailable &&
    availableDateforNextBooking &&
    availableDateforNextBooking !== "0000-00-00" &&
    availableDateforNextBooking !== null
  ) {
    const availableDate = new Date(availableDateforNextBooking);
    const today = new Date();

    today.setHours(0, 0, 0, 0);
    availableDate.setHours(0, 0, 0, 0);

    if (availableDate > today) {
      return `Available from ${availableDate.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      })}`;
    }
  }

  return "Available from Tomorrow";
};

const getAvailabilityDate = (flat) => {
  // Priority 1: Use availableDate if it's a Date object
  if (flat.availableDate instanceof Date) {
    return flat.availableDate;
  }

  // Priority 2: Use availableDate if it's a valid date string
  if (flat.availableDate) {
    const date = new Date(flat.availableDate);
    if (!isNaN(date.getTime())) {
      return date;
    }
  }

  // Priority 3: Parse availableFrom string
  if (flat.availableFrom) {
    const availableText = flat.availableFrom.toLowerCase().trim();
    
    // Check for "tomorrow" or "available from tomorrow"
    if (availableText.includes('tomorrow')) {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      return tomorrow;
    }
    
    // Check for "today" or "available from today"
    if (availableText.includes('today')) {
      return new Date();
    }
    
    // Try to extract date from "Available from DD/MM/YYYY" format
    const dateMatch = availableText.match(/(\d{1,2}\/\d{1,2}\/\d{4})/);
    if (dateMatch) {
      const dateParts = dateMatch[1].split('/');
      // DD/MM/YYYY format
      const day = parseInt(dateParts[0], 10);
      const month = parseInt(dateParts[1], 10) - 1; // Month is 0-indexed
      const year = parseInt(dateParts[2], 10);
      const date = new Date(year, month, day);
      if (!isNaN(date.getTime())) {
        return date;
      }
    }
  }

  // Priority 4: Use available_date_for_next_booking from raw flat data
  if (flat.available_date_for_next_booking && flat.available_date_for_next_booking !== "0000-00-00") {
    const date = new Date(flat.available_date_for_next_booking);
    if (!isNaN(date.getTime())) {
      return date;
    }
  }

  // Fallback: Return far future date for flats without availability info
  return new Date('2099-12-31');
};

// Optimized: Computed property for filtered and sorted flats with early returns
const availableFlats = computed(() => {
  // Early return if no flats
  if (!allFlats.value.length) return [];
  
  let filtered = allFlats.value;

  // Combine filters into single pass for better performance
  if (
    (selectedBalcony.value && selectedBalcony.value !== "Balcony") ||
    (selected.value && selected.value !== "Flat Type") ||
    (selectedFurnishing.value && selectedFurnishing.value !== "Furnishing")
  ) {
    filtered = filtered.filter(flat => {
      // Balcony filter
  if (selectedBalcony.value && selectedBalcony.value !== "Balcony") {
        if (flat.balconyType !== selectedBalcony.value) return false;
  }

      // Flat type filter
  if (selected.value && selected.value !== "Flat Type") {
        if (flat.type !== selected.value) return false;
  }

      // Furnishing filter
  if (selectedFurnishing.value && selectedFurnishing.value !== "Furnishing") {
        if (flat.furnished !== selectedFurnishing.value) return false;
      }
      
      return true;
    });
  }

  // Filter by availability date (only if user has actively selected a date)
  if (selectedDate.value && dateFilterActive.value) {
      const selectedDateObj = new Date(selectedDate.value);
      selectedDateObj.setHours(0, 0, 0, 0); // Normalize to start of day
      
    filtered = filtered.filter(flat => {
      // Use the existing getAvailabilityDate function which handles all date formats correctly
      const flatAvailableDate = getAvailabilityDate(flat);
      
      // Normalize to start of day for accurate comparison
      const normalizedFlatDate = new Date(flatAvailableDate);
      normalizedFlatDate.setHours(0, 0, 0, 0);
      
      // Include flats that are available on or before the selected date
      // Exclude flats with far future dates (2099-12-31) which indicate no availability info
      const farFutureDate = new Date('2099-12-31');
      if (normalizedFlatDate.getTime() === farFutureDate.getTime()) {
        return false; // Exclude flats without availability info
      }
      
      return normalizedFlatDate <= selectedDateObj;
    });
  }

  // Apply sorting only if needed
  if (selectedSortby.value && selectedSortby.value !== "Sort By") {
    // Create shallow copy only when sorting is needed
    const toSort = [...filtered];
    
    switch (selectedSortby.value) {
      case "Flats Availability Sooner":
        toSort.sort((a, b) => {
          const dateA = getAvailabilityDate(a);
          const dateB = getAvailabilityDate(b);
          return dateA.getTime() - dateB.getTime();
        });
        break;
        
      case "Flats Availability Later":
        toSort.sort((a, b) => {
          const dateA = getAvailabilityDate(a);
          const dateB = getAvailabilityDate(b);
          return dateB.getTime() - dateA.getTime();
        });
        break;
        
      case "Rent: Low to High":
        toSort.sort((a, b) => {
          const rentA = parseFloat(a.rent.replace(/[₹,]/g, ''));
          const rentB = parseFloat(b.rent.replace(/[₹,]/g, ''));
          return rentA - rentB;
        });
        break;
        
      case "Rent: High to Low":
        toSort.sort((a, b) => {
          const rentA = parseFloat(a.rent.replace(/[₹,]/g, ''));
          const rentB = parseFloat(b.rent.replace(/[₹,]/g, ''));
          return rentB - rentA;
        });
        break;
    }
    
    return toSort;
  }

  return filtered;
});

// Computed property for available flat types (for display in property header)
const availableFlatTypes = computed(() => {
  if (!property.value) return [];
  
  const availableTypes = [];
  
  // Check each availability field and add corresponding flat type
  if (property.value.studioAvailability) {
    availableTypes.push('Studio');
  }
  if (property.value.bhk1Availability) {
    availableTypes.push('1 BHK');
  }
  if (property.value.bhk2Availability) {
    availableTypes.push('2 BHK');
  }
  if (property.value.bhk3Availability) {
    availableTypes.push('3 BHK');
  }
  
  
  return availableTypes;
});

// Computed properties for filter options
const flatTypes = computed(() => {
  if (!property.value?.flats) return [];
  const types = [
    ...new Set(property.value.flats.map((flat) => flat.flat_type)),
  ];
  return types.map((type) => ({ label: type, value: type }));
});

const balconyTypes = computed(() => {
  if (!allFlats.value.length) return [];
  const types = [
    ...new Set(allFlats.value.map((flat) => flat.balconyType)),
  ];
  return types.map((type) => ({
    label: type,
    value: type,
    id: allFlats.value.find((f) => f.balconyType === type)?.balconyId,
  }));
});

const furnishingTypes = computed(() => {
  if (!property.value?.flats) return [];
  const types = [
    ...new Set(property.value.flats.map((flat) => flat.furnishing_type)),
  ];
  return types.map((type) => ({
    label: getFurnishTypeLabel(type),
    value: getFurnishTypeData(type),
    id: type,
  }));
});

function selectLocality(loc) {
  selected.value = loc;
  isOpenLocality.value = false;
}

function selectFurnishing(locfur) {
  selectedFurnishing.value = locfur;
  isOpenFurnishing.value = false;
}

function selectBalcony(locbal) {
  selectedBalcony.value = locbal;
  isOpenBalcony.value = false;
}

function loadBalconies() {
  balconyLoading.value = true;
  balconyError.value = null;
  // Balconies are loaded from property data, so just simulate loading
  setTimeout(() => {
    balconyLoading.value = false;
  }, 500);
}
function selectSortby(option) {
  selectedSortby.value = option;
  isOpenSortby.value = false;
}
// Use dynamic data from computed properties
const localities = computed(() => [
  { label: "Flat Type", value: "" },
  ...flatTypes.value,
]);

const furnishing = computed(() => [
  { label: "Furnishing", value: "" },
  ...furnishingTypes.value,
]);

const balcony = computed(() => [
  { label: "Balcony", value: "" },
  ...balconyTypes.value,
]);

const selectedBalconyLabel = computed(() => {
  return selectedBalcony.value || "Balcony";
});

// Pagination for flats
const visibleFlatsCount = ref(5)
const FLATS_PER_PAGE = 5

// Computed property for displayed flats - shows all loaded flats
const displayedFlats = computed(() => {
  // Show all available flats (no client-side pagination since we're using API pagination)
  return availableFlats.value
})

// Check if there are more flats to show
const hasMoreFlats = computed(() => {
  // Use totalAvailableFlats from API if available, otherwise use availableFlats.length
  const totalCount = totalAvailableFlats.value !== null && totalAvailableFlats.value !== undefined 
    ? totalAvailableFlats.value 
    : availableFlats.value.length;
  
  return totalCount > availableFlats.value.length;
})

// Load more flats function - calls API with pagination
const loadMoreFlats = async () => {
  if (isLoadingMoreFlats.value) return; // Prevent multiple simultaneous calls
  
  try {
    isLoadingMoreFlats.value = true;
    
    // Prepare auth data with offset and limit for pagination
    const authData = {
      city: city,
      area: area,
      property_slug: propertySlug,
      offset: flatsOffset.value,
      limit: 5, // Load 5 more flats each time
    };

    const response = await resolveFriendlyUrl(propertySlug, authData);
    
    if (response.status === "success" && response.flats && Array.isArray(response.flats)) {
      // Append new flats to existing flats array
      if (property.value && property.value.flats) {
        // Append new flats to the existing array - Vue reactivity will automatically update the display
        property.value.flats = [...property.value.flats, ...response.flats];
      } else if (property.value) {
        // If flats array doesn't exist yet, create it
        property.value.flats = response.flats;
      }
      
      // Update offset for next load
      flatsOffset.value += 5;
      
      // Update total available flats if provided
      if (response.availableFlats !== null && response.availableFlats !== undefined) {
        totalAvailableFlats.value = response.availableFlats;
      }
    }
  } catch (error) {
    console.error('Error loading more flats:', error);
  } finally {
    isLoadingMoreFlats.value = false;
  }
}

// ✅ Call API when filters change
const isLoadingFilteredFlats = ref(false);

// Helper function to get furnishing type code from label
const getFurnishTypeCodeFromLabel = (label) => {
  if (!label || label === 'Furnishing') return undefined;
  const normalized = label.toLowerCase().trim();
  if (normalized.includes('fully furnished ac') || normalized === 'fully furnished ac') {
    return '2';
  } else if (normalized.includes('fully furnished') || normalized === 'fully furnished') {
    return '1';
  } else if (normalized.includes('semi') || normalized === 'semi-furnished') {
    return '3';
  }
  return undefined;
};

// Function to call API with filter parameters
const loadFilteredFlats = async () => {
  if (isLoadingFilteredFlats.value || !property.value) return;
  
  try {
    isLoadingFilteredFlats.value = true;
    
    // Prepare filter parameters - match the API structure from user's example
    const authData = {
      city: city,
      area: area,
      property_slug: propertySlug,
      slug: propertySlug,
      // No limit parameter - API will return all matching results
    };
    
    // Add flatType filter if selected
    if (selected.value && selected.value !== "Flat Type") {
      authData.flatType = selected.value;
    }
    
    // Add furnishing filter if selected
    if (selectedFurnishing.value && selectedFurnishing.value !== "Furnishing") {
      const furnishCode = getFurnishTypeCodeFromLabel(selectedFurnishing.value);
      if (furnishCode) {
        authData.furnish_type = furnishCode;
      }
    }
    
    // Add balcony filter if selected
    if (selectedBalcony.value && selectedBalcony.value !== "Balcony") {
      authData.balconyType = selectedBalcony.value;
    }
    
    // Add available date filter if selected
    if (selectedDate.value && dateFilterActive.value) {
      try {
        const date = new Date(selectedDate.value);
        if (!isNaN(date.getTime())) {
          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');
          authData.available_date_for_next_booking = `${year}-${month}-${day}`;
        }
      } catch (e) {
        // If date parsing fails, skip
      }
    }
    
    // Add sortBy filter if selected
    if (selectedSortby.value && selectedSortby.value !== "Sort By") {
      authData.sortby = selectedSortby.value;
    }
    
    // Call API
    const response = await resolveFriendlyUrl(propertySlug, authData);
    
    if (response.status === "success" && response.flats) {
      // Update property flats with filtered results
      if (property.value) {
        property.value.flats = response.flats;
      }
      
      // Update total available flats count if provided
      if (response.availableFlats !== null && response.availableFlats !== undefined) {
        totalAvailableFlats.value = response.availableFlats;
      }
      
      // Reset pagination offset
      flatsOffset.value = 5;
    } else {
      // No results - set empty array
      if (property.value) {
        property.value.flats = [];
      }
      totalAvailableFlats.value = 0;
    }
  } catch (error) {
    console.error('Error loading filtered flats:', error);
    // On error, set empty array
    if (property.value) {
      property.value.flats = [];
    }
    totalAvailableFlats.value = 0;
  } finally {
    isLoadingFilteredFlats.value = false;
  }
};

// Watch for filter changes and call API
watch([selected, selectedFurnishing, selectedBalcony, selectedDate, selectedSortby], () => {
  // Only call API if filters are actually selected (not default values)
  const hasActiveFilters = 
    (selected.value && selected.value !== "Flat Type") ||
    (selectedFurnishing.value && selectedFurnishing.value !== "Furnishing") ||
    (selectedBalcony.value && selectedBalcony.value !== "Balcony") ||
    (selectedDate.value && dateFilterActive.value) ||
    (selectedSortby.value && selectedSortby.value !== "Sort By");
  
  if (hasActiveFilters && property.value) {
    loadFilteredFlats();
  }
}, { deep: true });

// Reset pagination when filters change
watch(() => availableFlats.value, () => {
  visibleFlatsCount.value = FLATS_PER_PAGE
  // Reset offset when filters change
  flatsOffset.value = 5;
}, { deep: true })

// Computed property to check if any filters are active
const hasActiveFilters = computed(() => {
  return (
    (selected.value && selected.value !== "Flat Type") ||
    (selectedFurnishing.value && selectedFurnishing.value !== "Furnishing") ||
    (selectedBalcony.value && selectedBalcony.value !== "Balcony") ||
    (selectedDate.value && dateFilterActive.value) ||
    (selectedSortby.value && selectedSortby.value !== "Sort By")
  );
});

const sortOptions = computed(() => {
  const options = ["Sort By"];
  
  // Only add availability sorting if we have flats with availability data
  if (allFlats.value.some(flat => flat.availableDate || flat.availableFrom)) {
    options.push("Flats Availability Sooner", "Flats Availability Later");
  }
  
  // Only add rent sorting if we have flats with rent data
  if (allFlats.value.some(flat => flat.rent)) {
    options.push("Rent: Low to High", "Rent: High to Low");
  }
  
  return options;
});

// Computed property to generate location URL
const locationURL = computed(() => {
  if (!property.value) return "#";
  return generateLocationURL(
    property.value.user_friendly_url,
    property.value.slug
  );
});

// Helper function to generate location URL based on PHP logic
const generateLocationURL = (userFriendlyUrl, propertySlug) => {
  if (!userFriendlyUrl || !propertySlug) return "#";
  let locationURL = userFriendlyUrl.replace(`/${propertySlug}`, "");
  locationURL = locationURL.replace(/\//g, "/flats-for-rent-in-");
  if (!locationURL.startsWith("/")) {
    locationURL = "/" + locationURL;
  }
  return locationURL;
};

// END OF COMPUTED PROPERTIES

// Set component ready after mount to prevent temporal dead zone issues
onMounted(() => {
  componentReady.value = true;
});

// Computed property for date display
const dateDisplayLabel = computed(() => {
  return 'Move-in date'
})

// Dynamic dropdown positioning based on screen size
const dropdownPosition = computed(() => {
  if (typeof window !== 'undefined') {
    if (window.innerWidth < 404) {
      return 'left-[0em]' // Mobile: dropdown to the left
    } else if (window.innerWidth >= 404 ) {
      return 'left-[-6em]' // Tablet: dropdown to the right
    } else {
      return 'left-[0em]' // Desktop: dropdown to the left
    }
  }
  return 'left-[0em]' // Default fallback
})
// Modal state
const isModalOpen = ref(false);
const currentImageIndex = ref(0);


// REPLACEABLE BLOCK: pages query → state hydrator (REPLACE)
const filterKey = ref(0)
const routeQ = useRoute()

const resetToDefaults = async () => {
  selected.value = "Flat Type"
  selectedFurnishing.value = "Furnishing"
  selectedBalcony.value = "Balcony"
  selectedSortby.value = "Sort By"
  dateFilterActive.value = false
  selectedDate.value = today.toISOString().slice(0, 10) // Reset to today's date
  
  // Reload original flats without filters
  if (property.value) {
    try {
      isLoadingFilteredFlats.value = true;
      const authData = {
        city: city,
        area: area,
        property_slug: propertySlug,
        slug: propertySlug,
        limit: 6, // Initial limit
      };
      
      const response = await resolveFriendlyUrl(propertySlug, authData);
      if (response.status === "success" && response.flats) {
        property.value.flats = response.flats;
        if (response.availableFlats !== null && response.availableFlats !== undefined) {
          totalAvailableFlats.value = response.availableFlats;
        }
        flatsOffset.value = 5;
      }
    } catch (error) {
      console.error('Error resetting filters:', error);
    } finally {
      isLoadingFilteredFlats.value = false;
    }
  }
}

const hydrateFromQuery = () => {
  const q = routeQ.query
  if (!q || Object.keys(q).length === 0) {
    resetToDefaults()
    return
  }
  if (q.type)       selected.value = String(q.type)
  if (q.furnishing) selectedFurnishing.value = String(q.furnishing)
  if (q.balcony)    selectedBalcony.value = String(q.balcony)
  if (q.sort)       selectedSortby.value = String(q.sort)
}

onMounted(() => {
  hydrateFromQuery()
})

watch(
  () => routeQ.query,
  async () => {
    hydrateFromQuery()
    filterKey.value++
    await nextTick()
    if (typeof updateScrollButtons === 'function') updateScrollButtons()
  }
)
// REPLACEABLE BLOCK END

// Reset pagination when filterKey changes (filter/sort updates)
watch(() => filterKey.value, () => {
  visibleFlatsCount.value = FLATS_PER_PAGE
})



// Modal functions
const openModal = (index) => {
  currentImageIndex.value = index;
  isModalOpen.value = true;
  document.body.style.overflow = "hidden"; // Prevent body scroll
};

const closeModal = () => {
  isModalOpen.value = false;
  document.body.style.overflow = "auto"; // Restore body scroll
};

// Helper function to extract YouTube video ID from URL
const getYouTubeVideoId = (url) => {
  if (!url) return null;
  
  // Handle different YouTube URL formats
  const patterns = [
    // youtu.be/VIDEO_ID
    /(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})/,
    // youtube.com/watch?v=VIDEO_ID
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})/,
    // youtube.com/embed/VIDEO_ID
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
    // youtube.com/v/VIDEO_ID
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})/,
    // youtube.com/watch?v=VIDEO_ID&other_params
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})/
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match && match[1]) {
      return match[1];
    }
  }
  
  return null;
};

// Helper function to get YouTube thumbnail URL
const getYouTubeThumbnail = (url) => {
  if (!url) {
    console.warn('getYouTubeThumbnail: No URL provided');
    return null;
  }
  
  const videoId = getYouTubeVideoId(url);
  if (!videoId) {
    console.warn('getYouTubeThumbnail: Could not extract video ID from URL:', url);
    return null;
  }
  
  const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
  //console.log('Generated YouTube thumbnail URL:', thumbnailUrl, 'from:', url);
  
  return thumbnailUrl;
};

// Handle image loading errors for YouTube thumbnails
const handleImageError = (event, mediaItem) => {
  if (mediaItem.type === 'youtube') {
    const img = event.target;
    const videoId = getYouTubeVideoId(mediaItem.watchUrl || mediaItem.url);
    
    if (!videoId) return;
    
    // Try different thumbnail qualities if the current one fails
    const currentSrc = img.src;
    
    if (currentSrc.includes('hqdefault.jpg')) {
      // Fallback to medium quality
      img.src = `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
    } else if (currentSrc.includes('mqdefault.jpg')) {
      // Fallback to default quality
      img.src = `https://img.youtube.com/vi/${videoId}/default.jpg`;
    } else if (currentSrc.includes('default.jpg')) {
      // Last fallback - use a placeholder or the video icon
      img.src = 'https://kots-world.b-cdn.net/Final/assets/images/video-square.png';
    }
  }
};

// Helper function to convert embed URL to watch URL
const convertEmbedToWatchUrl = (embedUrl) => {
  if (!embedUrl) return "";

  // Extract video ID from embed URL
  // Format: https://www.youtube.com/embed/BndQqNm87Mc?si=PnfNcrb-EhcxnU5T
  const match = embedUrl.match(/\/embed\/([a-zA-Z0-9_-]+)/);
  if (match && match[1]) {
    return `https://www.youtube.com/watch?v=${match[1]}`;
  }

  // If it's already a watch URL, return as is
  if (embedUrl.includes("watch?v=")) {
    return embedUrl;
  }

  return embedUrl;
};

// Helper function to get total media count (images + videos)
const getTotalMediaCount = () => {
  if (!property.value) {
    return 0;
  }

  if (property.value.media) {
    return property.value.media.length;
  }
  return property.value.images ? property.value.images.length : 0;
};

// Toggle mobile details visibility
const toggleMobileDetails = () => {
  showMobileDetails.value = !showMobileDetails.value;
};

// Helper function to get current media item
const getCurrentMediaItem = () => {
  // Return a default item if property is not loaded yet
  if (!property.value) {
    return {
      type: "image",
      url: "",
    };
  }

  if (property.value.media && property.value.media.length > 0) {
    return (
      property.value.media[currentImageIndex.value] || {
        type: "image",
        url: "",
      }
    );
  }

  if (property.value.images && property.value.images.length > 0) {
    return {
      type: "image",
      url: property.value.images[currentImageIndex.value] || "",
    };
  }

  // Fallback if no media is available
  return {
    type: "image",
    url: "",
  };
};

const nextImage = () => {
  const totalCount = getTotalMediaCount();
  if (currentImageIndex.value < totalCount - 1) {
    currentImageIndex.value++;
  } else {
    currentImageIndex.value = 0; // Loop back to first image
  }
};

const previousImage = () => {
  const totalCount = getTotalMediaCount();
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--;
  } else {
    currentImageIndex.value = totalCount - 1; // Loop to last image
  }
};

const handleKeydown = (event) => {
  if (!isModalOpen.value) return;
  switch (event.key) {
    case "Escape":
      closeModal();
      break;
    case "ArrowLeft":
      previousImage();
      break;
    case "ArrowRight":
      nextImage();
      break;
  }
};

function goBack() {
  // More robust back navigation for iPhone Safari
  const referrer = document.referrer;
  const currentHost = window.location.host;
  
  // Check if we came from the same site
  if (referrer && referrer.includes(currentHost)) {
    // Try to go back using router with timeout fallback
    let backHandled = false;
    
    // Set a timeout to handle cases where router.back() hangs
    const fallbackTimeout = setTimeout(() => {
      if (!backHandled) {
        // console.warn('Router back timed out, using fallback');
        goToFallbackPage();
        backHandled = true;
      }
    }, 1000); // 1 second timeout
    
    try {
    router.back();
      // Clear timeout if back was successful
      setTimeout(() => {
        clearTimeout(fallbackTimeout);
        backHandled = true;
      }, 100);
    } catch (error) {
      // console.warn('Router back failed, using fallback:', error);
      clearTimeout(fallbackTimeout);
      if (!backHandled) {
        goToFallbackPage();
        backHandled = true;
      }
    }
  } else {
    // No referrer or external referrer - go to logical parent page
    goToFallbackPage();
  }
}

function goToFallbackPage() {
  const route = useRoute();
  const city = route.params.city;
  const area = route.params.area;
  
  // Construct logical parent URL based on current route structure
  if (area && area !== 'bangalore') {
    // Go to area-specific listings page
    router.push(`/flats-for-rent-in-${area}`);
  } else if (city) {
    // Go to city-specific listings page  
    router.push(`/flats-for-rent-in-${city}`);
  } else {
    // Go to main listings page
    router.push('/flats-for-rent-in-bangalore');
  }
}

// Add keyboard event listener only on client
onMounted(() => {
  document.addEventListener("keydown", handleKeydown);
});
onUnmounted(() => {
  document.removeEventListener("keydown", handleKeydown);
});

// Removed hardcoded properties array - now using API data only via carouselProperties

// ✅ SSR: Fetch property data on server-side for initial render
const { data: propertyData, pending: propertyLoading, error: propertyError } = await useAsyncData(
  `property-${city}-${area}-${propertySlug}`,
  async () => {
    try {
      // Create slug from URL parameters - pass as structured data in authData
      const slugData = { city: city, area: area, slug: propertySlug };

      // Add your auth data here if needed, including the slug structure
      const authData = {
        // Add authentication data that matches your PHP authArr
        city: city,
        area: area,
        property_slug: propertySlug,
        limit: 6, // Limit flats to 5 for initial load
        // token: 'your-token',
        // userId: 'user-id',
        // etc.
      };

      const response = await resolveFriendlyUrl(propertySlug, authData);
      if (response.status === "success") {
        // Store API meta data for later use (after property is set)
        if (response.meta?.title || response.meta?.description) {
          // Store in a temporary variable for later use
          globalThis.__apiMeta = response.meta;
        }

        // Handle flat page
        if (response.params?.flat_slug) {
          await navigateTo(`/flat/${response.params.flat_slug}`);
          return null;
        }

        // Handle property page - Transform API response to match component expectations
        if (response.params?.property_slug || response.name) {
          // Transform API response to property object format
          const transformedProperty = {
          id: response.property_id,
          title: response.name,
          slug: response.params?.property_slug || propertySlug,
          area: (response.location_slug || response.locationSlug || area || "").toUpperCase(),
          description: response.description,
          rent: `₹ ${parseFloat(response.rentStartsFrom).toLocaleString(
            "en-IN"
          )}/mo.`,
          type: "Studio, 1 BHK", // You might want to get this from a separate API call
          
          // Store API meta data for later reference
          apiMeta: response.meta || null,

          // Handle images - create media array with both image and video
          images: (() => {
            // Handle different possible structures for savedName
            if (!response.savedName) return [];
            
            // If it's already an array
            if (Array.isArray(response.savedName)) {
              return response.savedName.map((img) =>
                typeof img === 'string' 
                  ? `https://kots-world.b-cdn.net/Final/categoryImages/thumb/${img}`
                  : `https://kots-world.b-cdn.net/Final/categoryImages/thumb/${img.savedName}`
              );
            }
            
            // If it's a single object
            if (typeof response.savedName === 'object' && response.savedName.savedName) {
              return [`https://kots-world.b-cdn.net/Final/categoryImages/thumb/${response.savedName.savedName}`];
            }
            
            // If it's a single string
            if (typeof response.savedName === 'string') {
              return [`https://kots-world.b-cdn.net/Final/categoryImages/thumb/${response.savedName}`];
            }
            
            return [];
          })(),

          // Create media array combining images and videos
          media: [
            // Add images with both full and thumb URLs
            ...(() => {
              if (!response.savedName) return [];
              
              // If it's already an array
              if (Array.isArray(response.savedName)) {
                return response.savedName.map((img) => ({
                  type: "image",
                  url: typeof img === 'string'
                    ? `https://kots-world.b-cdn.net/Final/categoryImages/full/${img}`
                    : `https://kots-world.b-cdn.net/Final/categoryImages/full/${img.savedName}`,
                  thumbUrl: typeof img === 'string'
                    ? `https://kots-world.b-cdn.net/Final/categoryImages/thumb/${img}`
                    : `https://kots-world.b-cdn.net/Final/categoryImages/full/${img.savedName}`,
                  originalName: typeof img === 'object' ? img.originalName : img,
                  savedName: typeof img === 'string' ? img : img.savedName,
                }));
              }
              
              // If it's a single object
              if (typeof response.savedName === 'object' && response.savedName.savedName) {
                return [{
                  type: "image",
                  url: `https://kots-world.b-cdn.net/Final/categoryImages/full/${response.savedName.savedName}`,
                  thumbUrl: `https://kots-world.b-cdn.net/Final/categoryImages/thumb/${response.savedName.savedName}`,
                  originalName: response.savedName.originalName,
                  savedName: response.savedName.savedName,
                }];
              }
              
              // If it's a single string
              if (typeof response.savedName === 'string') {
                return [{
                  type: "image",
                  url: `https://kots-world.b-cdn.net/Final/categoryImages/full/${response.savedName}`,
                  thumbUrl: `https://kots-world.b-cdn.net/Final/categoryImages/thumb/${response.savedName}`,
                  originalName: response.savedName,
                  savedName: response.savedName,
                }];
              }
              
              return [];
            })(),
            // Add YouTube video if available
            ...(response.youtube_link
              ? [
                  {
                    type: "youtube",
                    url: response.youtube_link, // Keep original embed URL for iframe
                    watchUrl: convertEmbedToWatchUrl(response.youtube_link), // For thumbnail generation
                  },
                ]
              : []),
          ],

          // Additional properties from API
          locationDescription: response.locationDescription,
          localityDescription: response.localityDescription,
          location: response.location,
          mapDescription: response.mapDescription,
          virtualTour: response.virtualTour,
          youtube_link: response.youtube_link,
          featuredImage: response.featuredImage,
          user_friendly_url: response.user_friendly_url,
          studioAvailability: response.studioAvailability,
          bhk1Availability: response.bhk1Availability,
          bhk2Availability: response.bhk2Availability,
          bhk3Availability: response.bhk3Availability,
          flats: response.flats || [],
            // Nearby locations from API response (array of strings or null)
            nearbyPlaces: response.nearbyPlaces || response.nearby_places || null,
          };
          
          return {
            property: transformedProperty,
            availableFlats: response.availableFlats || null,
            nearbyPlaces: transformedProperty.nearbyPlaces || null,
            isCategoryPage: false
          };
        }

      // Handle other cases (locality filters, etc.)
      if (response.params?.locality) {
        // Set locality filter
      }
      if (response.params?.flatType) {
        // Set flat type filter
      }
      if (response.params?.furnishingType) {
        // Set furnishing filter
      }
      if (response.params?.balconyType) {
        // Set balcony filter
      }
      if (response.params?.parkingType) {
        // Set parking filter
      }
      } else {
        // Check if this might be a category slug before throwing error
        const categoryInfo = parseCategory(propertySlug);
        if (categoryInfo) {
          return {
            property: null,
            availableFlats: null,
            nearbyPlaces: null,
            isCategoryPage: true,
            categoryInfo: categoryInfo
          };
        }
        throw new Error("Invalid API response");
      }
    } catch (error) {
      // Check if this is a category slug instead of a property slug
      const categoryInfo = parseCategory(propertySlug);
      
      if (categoryInfo) {
        return {
          property: null,
          availableFlats: null,
          nearbyPlaces: null,
          isCategoryPage: true,
          categoryInfo: categoryInfo
        };
      }
      
      // No fallback - show 404 error
      throw createError({
        statusCode: 404,
        statusMessage: "Property not found",
      });
    }
  },
  {
    server: true,      // ✅ SSR: Fetch on server
    lazy: false,       // Block render until data arrives (good for SEO)
    default: () => ({ property: null, availableFlats: null, nearbyPlaces: null, isCategoryPage: false })
  }
);

// ✅ SSR: Initialize property data from SSR response
if (propertyData.value) {
  if (propertyData.value.isCategoryPage && propertyData.value.categoryInfo) {
    // Handle category page
    const categoryInfo = propertyData.value.categoryInfo;
    isCategoryPage.value = true;
    categoryType.value = categoryInfo.type;
    categoryValue.value = categoryInfo.value;
    
    // Set up category page filters (client-side only)
    if (process.client) {
      const { useUiStore } = await import('~/stores/ui');
      const ui = useUiStore();
      
      const searchFilters = {
        location: slugToTitle(area),
        locationSlug: area.toLowerCase().replace(/\s+/g, '-'),
        locality: slugToTitle(area),
        flatType: categoryInfo.type === 'flatType' ? categoryInfo.value : '',
        furnishing: categoryInfo.type === 'furnishing' ? categoryInfo.value : '',
        balcony: categoryInfo.type === 'balcony' ? categoryInfo.value : '',
        parking: categoryInfo.type === 'parking' ? categoryInfo.value : '',
        moveInDate: '',
        userLatitude: null,
        userLongitude: null,
        isNearMe: false,
        sortBy: ''
      };
      
      ui.updateSearchFilters(searchFilters);
      ui.setSearchActive(true);
      setCategorySEO(categoryInfo, area, city);
      
      // Track category page visit
      if (hasCampaignData()) {
        trackPropertyDetailVisit(String(propertySlug), String(area), String(city), 'landing')
      }
    }
  } else if (propertyData.value.property) {
    // Handle property page
    property.value = propertyData.value.property;
    
    // Set nearby places directly from API response if available
    if (property.value.nearbyPlaces && Array.isArray(property.value.nearbyPlaces) && property.value.nearbyPlaces.length > 0) {
      nearbyPlaces.value = property.value.nearbyPlaces;
    }
    
    // Store availableFlats count from API response
    totalAvailableFlats.value = propertyData.value.availableFlats || null;
    
    // Reset pagination offset when property is loaded (initial load is 6, so next offset is 5)
    flatsOffset.value = 5;
    
    // Track property detail page visit (client-side only)
    if (process.client && hasCampaignData()) {
      trackPropertyDetailVisit(String(propertySlug), String(area), String(city), 'property-detail')
    }
  }
}

// Reactive data for amenities
const amenities = ref([]);
const amenitiesLoading = ref(true);

// Initialize nearby places composable
const { getNearbyPlaces } = useNearbyPlaces();

// Helper function to get unique flat types from flats array
const getUniqueFlatTypes = (flats) => {
  if (!flats || !Array.isArray(flats)) return [];
  return [...new Set(flats.map((flat) => flat.flat_type || flat.flatType))];
};

// Helper function to format flat types in order (matching PHP logic)
const formatFlatTypes = (flatTypes) => {
  const sortedTypes = [];
  const studio = flatTypes.find((type) => ["studio", "Studio"].includes(type));
  const bhk1 = flatTypes.find((type) => type.includes("1"));
  const bhk2 = flatTypes.find(
    (type) => type.includes("2") && !type.includes("2.5")
  );
  const bhk25 = flatTypes.find((type) => type.includes("2.5"));
  const bhk3 = flatTypes.find((type) => type.includes("3"));
  const bhk4 = flatTypes.find((type) => type.includes("4"));

  if (studio) sortedTypes.push(studio);
  if (bhk1) sortedTypes.push(bhk1);
  if (bhk2) sortedTypes.push(bhk2);
  if (bhk25) sortedTypes.push(bhk25);
  if (bhk3) sortedTypes.push(bhk3);
  if (bhk4) sortedTypes.push(bhk4);

  return sortedTypes;
};

// Helper function to get availability badge info
const getAvailabilityBadge = (flatsCount) => {
  return {
    text:
      flatsCount < 10
        ? ` ${flatsCount} flats available`
        : `${flatsCount} flats available`,
    isLimited: flatsCount < 10,
    showFillingFast: flatsCount < 10,
  };
};

// ✅ SSR: Fetch carousel properties on server-side for initial render
const { data: carouselData, pending: carouselLoading } = await useAsyncData(
  `carousel-properties-${city}-${area}-${propertySlug}`,
  async () => {
    try {
      // Pass limit parameter to reduce API payload
      const apiResponse = await propertiesService.getPropertiesAndFlats(undefined, 5);
      
      if (apiResponse?.properties && apiResponse.properties.length > 0) {
        // Transform raw API properties for carousel display
        const transformedProperties = apiResponse.properties.map((property) => {
          // Use availableFlats count from API response
          const flatsCount = property.availableFlats || 0;

          // Get flat types from property flats if available
          let flatTypes = getUniqueFlatTypes(property.flats);
          if (flatTypes.length === 0) {
            // Default flat types if not available
            flatTypes = ["Studio", "1 BHK"];
          }

          return {
            id: property.id,
            name: property.name,
            location: property.displayLocation || property.location,
            userFriendlyUrl: property.user_friendly_url,
            rentStartsFrom: parseFloat(property.rentStartsFrom) || 0,
            flats: property.flats || [],
            flatsCount: flatsCount,
            flatTypes: flatTypes,
            formattedFlatTypes: formatFlatTypes(flatTypes),
            featuredImage: property.featuredImage,
            image: property.image,
            availabilityBadge: getAvailabilityBadge(flatsCount),
          };
        });
        
        return {
          properties: transformedProperties,
          propertyCount: apiResponse.propertyCount || null
        };
      } else {
        return {
          properties: [],
          propertyCount: null
        };
      }
    } catch (error) {
      console.error("Error loading carousel properties:", error);
      return {
        properties: [],
        propertyCount: null
      };
    }
  },
  {
    server: true,      // ✅ SSR: Fetch on server
    lazy: true,        // Non-blocking: Don't delay initial render
    default: () => ({ properties: [], propertyCount: null })
  }
);

// Reactive data for carousel properties (from SSR)
const carouselProperties = computed(() => carouselData.value?.properties || []);
const carouselPropertyCount = computed(() => carouselData.value?.propertyCount || null);

// Function to load amenities
const loadAmenities = async () => {
  try {
    amenitiesLoading.value = true;
    const featureItems = await amenitiesService.getFeatureItems();
    amenities.value = featureItems;
  } catch (error) {
    // console.error("Error loading amenities:", error);
    // Fallback amenities will be provided by the service
    amenities.value = [];
  } finally {
    amenitiesLoading.value = false;
  }
};


// ✅ Carousel properties are now loaded via useAsyncData above (SSR)
// No need for loadCarouselProperties() function anymore

// ✅ Property data is now fetched via useAsyncData above (SSR)
// No need to call resolveProperty() anymore - it's been replaced with useAsyncData

// Function to load nearby places from API response (non-blocking, async)
const loadNearbyPlaces = async () => {
  if (!property.value) return;
  
  try {
    nearbyPlacesLoading.value = true;
    
    // Use nearbyPlaces from API response if available
    if (property.value.nearbyPlaces && Array.isArray(property.value.nearbyPlaces) && property.value.nearbyPlaces.length > 0) {
      nearbyPlaces.value = property.value.nearbyPlaces;
      return;
    }
    
    // If not in API response, set to null (no fallback)
    nearbyPlaces.value = null;
  } catch (error) {
    console.warn('Error loading nearby places:', error);
    // Set to null on error
    nearbyPlaces.value = null;
  } finally {
    nearbyPlacesLoading.value = false;
  }
};

// Defer non-critical API calls to after initial render
onMounted(async () => {
  // Store property context (location and flat type) for WhatsApp messaging
  const { storePropertyContext, parsePropertyContextFromPath } = usePropertyContext();
  
  // Parse context from current URL path
  const currentPath = route.path || window.location.pathname;
  const context = parsePropertyContextFromPath(currentPath);
  
  if (context) {
    storePropertyContext(context);
    // console.log('✅ Property context stored:', context);
  }
  
  // Load amenities in the background (carousel properties are now SSR)
  loadAmenities().catch(error => {
    console.error('Error loading amenities:', error);
  });
  
  // Load nearby places after a short delay to prioritize other content
  setTimeout(() => {
    loadNearbyPlaces().catch(error => {
      console.warn('Error loading nearby places:', error);
    });
  }, 1000); // 1 second delay to not block initial render
});

// Helper function to get property address dynamically
const getPropertyAddress = (propertyData, area) => {
  // First try to use actual property data if available
  if (propertyData) {
    // Try to extract address from locationDescription or description
    let streetAddress = propertyData.location || propertyData.description || propertyData.localityDescription || propertyData.locationDescription || '';

    
    // If locationDescription exists, try to extract the first part as address
    // if (propertyData.description) {
    //   // Extract the first sentence or part before first period/comma that looks like an address
    //   const addressMatch = propertyData.description.match(/^[^.]*(?:Road|Layout|Main|Street|Cross|Rd|St)[^.,]*/i);
    //   if (addressMatch) {
    //     streetAddress = addressMatch[0].trim();
    //   } else {
    //     // If no clear address pattern, try to get area name and common address terms
    //     streetAddress = `${propertyData.title || 'KOTS Property'}, ${area || 'Bengaluru'}`;
    //   }
    // } else if (propertyData.description) {
    //   // Use property title and area as fallback
    //   streetAddress = `${propertyData.title || 'KOTS Property'}, ${area || 'Bengaluru'}`;
    // }
    
    // Get postal code based on area with fallbacks
    const postalCodeMap = {
      'whitefield': "560066",
      'hsr': "560102", 
      'sarjapur': "560035",
      'hennur': "560043",
      'mahadevpura': "560048",
      'marathahalli': "560037",
      'bellandur': "560103"
    };
    
    return {
      streetAddress: streetAddress || `${area}, Bengaluru`,
      postalCode: postalCodeMap[area?.toLowerCase()] || "560001",
      latitude: propertyData.latitude || null,
      longitude: propertyData.longitude || null
    };
  }
  
  // Fallback to static mapping if no property data
  const addresses = {
    'whitefield': {
      streetAddress: "68, Kots Abode, Pattandur Agrahara 2nd Main Rd, Maithri Layout",
      postalCode: "560066"
    },
    'hsr': {
      streetAddress: "56/2, 25th Cross Rd, 22nd A Main, Garden Layout, Sector 2", 
      postalCode: "560102"
    },
    'sarjapur': {
      streetAddress: "Sarjapur Road, Bengaluru",
      postalCode: "560035"
    },
    'hennur': {
      streetAddress: "Hennur Road, Bengaluru", 
      postalCode: "560043"
    },
    'mahadevpura': {
      streetAddress: "Mahadevpura, Bengaluru",
      postalCode: "560048"
    },
    'marathahalli': {
      streetAddress: "Marathahalli, Bengaluru",
      postalCode: "560037"
    },
    'bellandur': {
      streetAddress: "Bellandur, Bengaluru",
      postalCode: "560103"
    }
  };
  
  return addresses[area?.toLowerCase()] || {
    streetAddress: `${area}, Bengaluru`,
    postalCode: "560068"
  };
};

// Function to generate structured data
const generateStructuredData = () => {
  if (!property.value) return null;
  
  const currentUrl = `https://www.kots.world/${city}/${area}/${propertySlug}`;
  const metaImage = property.value.images?.[0] || "/images/main-logo.png";
  const apiMeta = globalThis.__apiMeta || property.value.apiMeta;
  const propertyAddress = getPropertyAddress(property.value, area);
  const areaName = area?.charAt(0).toUpperCase() + area?.slice(1).toLowerCase() || 'Bangalore';
  const rentAmount = property.value.rent?.replace(/[₹,\/mo.]/g, '').trim() || "25000";
  
  // Get flat types safely
  const flatTypes = availableFlatTypes.value?.length > 0 ? availableFlatTypes.value.join(', ') : property.value.type || 'Studio, 1 BHK';
  
  // Get total flats available
  const totalFlatsAvailable = totalAvailableFlats.value !== null && totalAvailableFlats.value !== undefined 
    ? totalAvailableFlats.value 
    : (availableFlats.value?.length || property.value.flats?.length || 0);
  
  // Get starting price (extract numeric value from rent string)
  const startingPrice = property.value.rent || `₹${rentAmount}/mo.`;
  
  // Get geo coordinates
  const latitude = property.value.latitude || propertyAddress.latitude;
  const longitude = property.value.longitude || propertyAddress.longitude;
  
  // Get video schema if YouTube video exists or virtual tour is available
  const hasYouTubeVideo = property.value.youtube_link;
  const hasVirtualTour = property.value.virtualTour;
  
  // Generate dynamic upload date in UTC format (as per schema.org standard)
  const getCurrentDateUTC = () => {
    try {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}T08:00:00+00:00`;
    } catch (error) {
      // Fallback to a fixed date if there's an error
      return "2025-01-09T08:00:00+00:00";
    }
  };
  
  // Ensure we have a valid thumbnail URL
  const getThumbnailUrl = () => {
    if (hasYouTubeVideo && getYouTubeThumbnail) {
      const ytThumbnail = getYouTubeThumbnail(hasYouTubeVideo);
      if (ytThumbnail) return ytThumbnail;
    }
    return metaImage || "https://www.kots.world/images/logo.png";
  };

  const videoSchema = (hasYouTubeVideo || hasVirtualTour) ? {
    "@type": "VideoObject",
    "name": hasYouTubeVideo ? 
      `${property.value.title || 'KOTS Property'} - Virtual Tour` : 
      `Virtual Tour of ${flatTypes} in ${areaName}`,
    "description": hasYouTubeVideo ?
      `Take a virtual tour of ${property.value.title || 'this premium property'} in ${areaName}, Bangalore. See the premium amenities and modern design of our managed rental apartments.` :
      `Take a 360° virtual tour of our premium ${flatTypes.toLowerCase()} for rent in ${areaName} under ₹${rentAmount}. Explore interiors, amenities, and nearby attractions.`,
    "thumbnailUrl": getThumbnailUrl(),
    "uploadDate": getCurrentDateUTC(),
    "duration": "PT2M45S",
    "contentUrl": hasYouTubeVideo ? currentUrl : (hasVirtualTour || currentUrl),
    "embedUrl": hasYouTubeVideo || hasVirtualTour,
    "publisher": {
      "@type": "Organization",
      "name": "KOTS World",
      "logo": {
        "@type": "ImageObject",
        "url": "https://www.kots.world/images/logo.png"
      }
    },
    "interactionStatistic": {
      "@type": "InteractionCounter",
      "interactionType": { "@type": "WatchAction" },
      "userInteractionCount": 1200
    },
    "isFamilyFriendly": "True",
    // Add both YouTube and Virtual Tour if both exist
    ...(hasYouTubeVideo && hasVirtualTour && {
      "hasPart": [
        {
          "@type": "VideoObject",
          "name": "YouTube Virtual Tour",
          "description": `YouTube virtual tour of ${property.value.title || 'this premium property'} in ${areaName}, Bangalore.`,
          "thumbnailUrl": getThumbnailUrl(),
          "uploadDate": getCurrentDateUTC(),
          "encodingFormat": "video/mp4",
          "contentUrl": hasYouTubeVideo
        },
        {
          "@type": "VideoObject",
          "name": "360° Virtual Tour View",
          "description": `Interactive 360° virtual tour of ${property.value.title || 'this premium property'} in ${areaName}, Bangalore.`,
          "thumbnailUrl": metaImage || "https://www.kots.world/images/logo.png",
          "uploadDate": getCurrentDateUTC(),
          "encodingFormat": "video/mp4",
          "contentUrl": hasVirtualTour
        }
      ]
    }),
    // Add only Virtual Tour if YouTube doesn't exist
    ...(hasVirtualTour && !hasYouTubeVideo && {
      "hasPart": {
        "@type": "VideoObject",
        "name": "360° Virtual Tour View",
        "description": `Interactive 360° virtual tour of ${property.value.title || 'this premium property'} in ${areaName}, Bangalore.`,
        "thumbnailUrl": metaImage || "https://www.kots.world/images/logo.png",
        "uploadDate": getCurrentDateUTC(),
        "encodingFormat": "video/mp4",
        "contentUrl": hasVirtualTour
      }
    }),
    "potentialAction": {
      "@type": "WatchAction",
      "target": hasYouTubeVideo || hasVirtualTour
    }
  } : null;

  // Build additionalProperty array for schema
  const additionalProperties = [
    {
      "@type": "PropertyValue",
      "name": "Total Flats Available",
      "value": String(totalFlatsAvailable)
    },
    {
      "@type": "PropertyValue",
      "name": "Starting Price",
      "value": startingPrice
    }
  ];

  // Add furnishing types to additionalProperty (PropertyValue is valid here)
  if (furnishingTypes.value && furnishingTypes.value.length > 0) {
    const uniqueFurnishingLabels = [
      ...new Set(
        furnishingTypes.value
          .filter((ft) => ft.label && ft.label !== "Furnishing") // Filter out default option
          .map((ft) => ft.label)
      )
    ];
    
    if (uniqueFurnishingLabels.length > 0) {
      additionalProperties.push({
        "@type": "PropertyValue",
        "name": "Furnishing",
        "value": uniqueFurnishingLabels.length === 1 
          ? uniqueFurnishingLabels[0] 
          : uniqueFurnishingLabels // Array if multiple types
      });
    }
  }

  // Add nearby locations if available (from API response)
  if (nearbyPlaces.value && Array.isArray(nearbyPlaces.value) && nearbyPlaces.value.length > 0) {
    additionalProperties.push({
      "@type": "PropertyValue",
      "name": "Nearby Locations",
      "value": nearbyPlaces.value
    });
  }

  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Apartment",
        "@id": currentUrl,
        "name": property.value.title,
        "description": apiMeta?.description || property.value.description || `Urban Gated Apartment in ${areaName}`,
        "url": currentUrl,
        "image": property.value.images || [metaImage],
        "brand": {
          "@type": "Organization",
          "name": "KOTS RENTING PRIVATE LIMITED"
        },
        "offers": {
          "@type": "Offer",
          "url": currentUrl,
          "priceCurrency": "INR",
          "price": rentAmount,
          "availability": "https://schema.org/InStock",
          "category": flatTypes
        },
        "address": {
          "@type": "PostalAddress",
          "streetAddress": propertyAddress.streetAddress || property.value.description || '',
          "addressLocality": areaName,
          "addressRegion": "Karnataka",
          // "postalCode": propertyAddress.postalCode,
          "addressCountry": "IN"
        },
        // Add geo coordinates if available
        ...(latitude && longitude && {
          "geo": {
            "@type": "GeoCoordinates",
            "latitude": parseFloat(String(latitude)),
            "longitude": parseFloat(String(longitude))
          }
        }),
        // Add additional properties (total flats, starting price, nearby locations)
        "additionalProperty": additionalProperties,
        "telephone": "+91-8550880555",
        "amenityFeature": [
          { "@type": "LocationFeatureSpecification", "name": "24/7 Tech Enabled Security" },
          { "@type": "LocationFeatureSpecification", "name": "24/7 Power & Water Backup" },
          { "@type": "LocationFeatureSpecification", "name": "Managed Housing" },
          { "@type": "LocationFeatureSpecification", "name": "Housekeeping Services" },
          { "@type": "LocationFeatureSpecification", "name": "High Speed Internet" },
          { "@type": "LocationFeatureSpecification", "name": "World Class Amenities" },
          { "@type": "LocationFeatureSpecification", "name": "Exclusive Addons" }
        ],
        ...(property.value.virtualTour && {
          "tourBookingPage": property.value.virtualTour
        }),
        ...(videoSchema && { "video": videoSchema }),
        "potentialAction": {
          "@type": "RentAction",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": currentUrl
          }
        }
      },
      {
        "@type": "Organization",
        "@id": "https://www.kots.world/#organization",
        "name": "KOTS RENTING PRIVATE LIMITED",
        "url": "https://www.kots.world/",
        "logo": {
          "@type": "ImageObject",
          "url": "https://www.kots.world/images/logo.png",
          "width": 180,
          "height": 60
        },
        "contactPoint": {
          "@type": "ContactPoint",
          "telephone": "+91-8550880555",
          "contactType": "customer service",
          "availableLanguage": ["English", "Hindi", "Kannada"]
        },
      },
      {
        "@type": "BreadcrumbList",
        "itemListElement": [
          {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": "https://www.kots.world/"
          },
          {
            "@type": "ListItem",
            "position": 2,
            "name": "Explore flats",
            "item": "https://www.kots.world/flats-for-rent-in-bangalore"
          },
          {
            "@type": "ListItem",
            "position": 3,
            "name": areaName,
            "item": `https://www.kots.world/flats-for-rent-in-${area}`
          }
          // {
          //   "@type": "ListItem",
          //   "position": 4,
          //   "name": property.value.title,
          //   "item": currentUrl
          // }
        ]
      },
      ...(availableFlats.value && availableFlats.value.length > 0 ? [{
        "@type": "ItemList",
        "@id": `${currentUrl}#flats`,
        "name": `Available Flats at ${property.value.title}`,
        "description": `${availableFlats.value.length} rental flats available in ${property.value.title}`,
        "numberOfItems": availableFlats.value.length,
        "itemListElement": availableFlats.value.slice(0, 5).map((flat, index) => ({
          "@type": "ListItem",
          "position": index + 1,
          "item": {
            "@type": "Apartment",
            "@id": `https://www.kots.world${flat.userFriendlyUrl}`,
            "name": flat.code,
            "url": `https://www.kots.world${flat.userFriendlyUrl}`,
            "offers": {
              "@type": "Offer",
              "price": flat.rent.replace(/[₹,]/g, ''),
              "priceCurrency": "INR",
              "availability": flat.availableFrom.includes('not Available') ? 
                "https://schema.org/OutOfStock" : "https://schema.org/InStock"
            },
            "category": flat.type,
            // Add furnishing as PropertyValue in additionalProperty (valid Schema.org format)
            ...(flat.furnished ? {
              "additionalProperty": [
                {
                  "@type": "PropertyValue",
                  "name": "Furnishing",
                  "value": flat.furnished
                }
              ]
            } : {})
          }
        }))
      }] : [])
    ]
  };
};

// Dynamic SEO Meta Tags and Structured Data for Property Pages - with API meta override (reactive)
const propertyCurrentUrl = computed(() => `https://www.kots.world/${city}/${area}/${propertySlug}`);

// Property page OG tags (only when property exists and it's NOT a category page)
const propertyOgTags = computed(() => {
  if (!property.value || isCategoryPage.value) {
    return { title: '', meta: [], link: [] };
  }
  
  const metaImage = property.value.images?.[0] || "/images/main-logo.png";
  const apiMeta = globalThis.__apiMeta || property.value.apiMeta;
  const areaName = area?.charAt(0).toUpperCase() + area?.slice(1).toLowerCase() || 'Bangalore';
  const flatTypes = availableFlatTypes.value?.length > 0 ? availableFlatTypes.value.join(' ') : property.value.type || 'Studio 1BHK';
  
  return useCompleteOgTags({
    title: apiMeta?.title || `${property.value.title} - ${flatTypes} in ${areaName} | KOTS`,
    description: apiMeta?.description || `${property.value.description || `Urban Gated Apartment in ${areaName}`}. ${flatTypes} starting from ${property.value.rent}. Book your premium apartment in ${areaName} with world-class amenities.`,
    image: metaImage,
    url: propertyCurrentUrl.value,
    type: 'website',
    siteName: 'KOTS'
  });
});

// Consolidated useHead for Property Pages (only when property exists and NOT category page)
useHead({
  title: computed(() => {
    // Only set title for property pages (not category pages)
    if (!property.value || isCategoryPage.value) return undefined;
    
    // Get title from OG tags or compute it directly
    const apiMeta = globalThis.__apiMeta || property.value.apiMeta;
    if (apiMeta?.title) return apiMeta.title;
    
    const areaName = area?.charAt(0).toUpperCase() + area?.slice(1).toLowerCase() || 'Bangalore';
    const flatTypes = availableFlatTypes.value?.length > 0 ? availableFlatTypes.value.join(' ') : property.value.type || 'Studio 1BHK';
    
    return propertyOgTags.value.title || `${property.value.title} - ${flatTypes} in ${areaName} | KOTS`;
  }),
  meta: computed(() => {
    if (!property.value || isCategoryPage.value) return [];
    
    const areaName = area?.charAt(0).toUpperCase() + area?.slice(1).toLowerCase() || 'Bangalore';
    const flatTypes = availableFlatTypes.value?.length > 0 ? availableFlatTypes.value.join(' ') : property.value.type || 'Studio 1BHK';
    
    return [
      ...propertyOgTags.value.meta,
      // Additional property-specific meta tags
      {
        name: 'keywords',
        content: `${property.value.title}, ${area} apartments, ${flatTypes}, furnished apartments ${area}, KOTS ${area}`
      }
    ];
  }),
  link: computed(() => {
    if (!property.value || isCategoryPage.value) return [];
    
    // Filter out canonical from ogTags since we're adding our own
    const ogLinksFiltered = propertyOgTags.value.link.filter(link => link.rel !== 'canonical');
    
    return [
      ...ogLinksFiltered,
      // Self-referring canonical tag
      { rel: 'canonical', href: propertyCurrentUrl.value },
      // Add preconnect for CDN performance
      { rel: 'preconnect', href: 'https://kots-world.b-cdn.net' },
      { rel: 'dns-prefetch', href: 'https://kots-world.b-cdn.net' }
    ];
  }),
  script: computed(() => {
    if (!property.value || isCategoryPage.value) return [];
    return [
      {
        type: 'application/ld+json',
        children: () => JSON.stringify(generateStructuredData()),
        key: 'structured-data'
      }
    ];
  })
});

// SEO Meta Tags for Category Pages (reactive - applies when isCategoryPage becomes true)
const currentUrl = computed(() => `https://www.kots.world/${city}/${area}/${propertySlug}`);

// Use dynamic computed properties for reactive meta tags
// These will update when filters change
const metaTitle = computed(() => {
  if (!isCategoryPage.value) return '';
  const flatType = dynamicCategoryName.value || 'Flat';
  const location = dynamicAreaName.value || slugToTitle(area) || 'Bangalore';
  return `Furnished ${flatType} Flat for Rent in ${location} | No Hidden Charges`;
});

// Computed property for meta title to use in alt tags (works for both property and category pages)
const metaTitleForAlt = computed(() => {
  // For category pages
  if (isCategoryPage.value) {
    return metaTitle.value;
  }
  
  // For property pages
  if (property.value) {
    const apiMeta = globalThis.__apiMeta || property.value.apiMeta;
    if (apiMeta?.title) return apiMeta.title;
    
    const areaName = area?.charAt(0).toUpperCase() + area?.slice(1).toLowerCase() || 'Bangalore';
    const flatTypes = availableFlatTypes.value?.length > 0 ? availableFlatTypes.value.join(' ') : property.value.type || 'Studio 1BHK';
    return `${property.value.title} - ${flatTypes} in ${areaName} | KOTS`;
  }
  
  return 'KOTS Property';
});

const metaDescription = computed(() => {
  if (!isCategoryPage.value) return '';
  const flatType = dynamicCategoryName.value || 'Flat';
  const location = dynamicAreaName.value || slugToTitle(area) || 'Bangalore';
  return `Check out Furnished ${flatType} Flats for Rent in ${location}, Bangalore at no hidden charges. Live Premium in Urban Gated Apartments with modern amenities, low deposit.`;
});

// Get complete OG tags using the composable with dynamic values (reactive)
const ogTags = computed(() => {
  if (!isCategoryPage.value) {
    return { title: '', meta: [], link: [] };
  }
  return useCompleteOgTags({
    title: metaTitle.value,
    description: metaDescription.value,
    image: 'https://www.kots.world/images/main-logo.png',
    url: currentUrl.value,
    type: 'website',
    siteName: 'KOTS'
  });
});

// Generate structured data for category pages (using dynamic values)
const generateCategoryStructuredData = () => {
  if (!isCategoryPage.value) return null;
  const flatType = dynamicCategoryName.value || categoryValue.value || slugToTitle(propertySlug);
  const location = dynamicAreaName.value || slugToTitle(area) || 'Bangalore';
  
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "BreadcrumbList",
        "@id": `${currentUrl.value}/#breadcrumbs`,
        itemListElement: [
          {
            "@type": "ListItem",
            position: 1,
            name: "Home",
            item: "https://www.kots.world/",
          },
          {
            "@type": "ListItem",
            position: 2,
            name: `Flats in ${location}`,
            item: area.toLowerCase() === "bangalore" ? `https://www.kots.world/flats-for-rent-in-${area.toLowerCase()}/` : `https://www.kots.world/bangalore/flats-for-rent-in-${area.toLowerCase()}/`
          },
          {
            "@type": "ListItem",
            position: 3,
            name: `${flatType} Flats for Rent in ${location}`,
            item: currentUrl.value,
          },
        ],
      },
      {
        "@type": "LocalBusiness",
        "@id": `${currentUrl.value}/#localbusiness`,
        name: "KOTS RENTING PRIVATE LIMITED",
        alternateName: "Kots",
        description: `Discover premium ${flatType.toLowerCase()} flats for rent in ${location}, Bangalore, with Kots. Featuring 24/7 security, power backup, high-speed internet, housekeeping, and world-class amenities.`,
        url: "https://www.kots.world/",
        logo: {
          "@type": "ImageObject",
          url: "https://www.kots.world/images/logo.png",
          width: 180,
          height: 60,
        },
        telephone: "+91-8550880555",
        email: "hello@kots.world",
        address: {
          "@type": "PostalAddress",
          streetAddress: "Multiple Locations",
          addressLocality: location,
          addressRegion: "Karnataka",
          postalCode: "560001",
          addressCountry: "IN",
        },
        geo: {
          "@type": "GeoCoordinates",
          latitude: "12.9716",
          longitude: "77.5946",
        },
        openingHours: "Mo-Su 00:00-23:59",
        priceRange: "₹₹₹",
        currenciesAccepted: "INR",
        paymentAccepted: ["Cash", "Credit Card", "Bank Transfer", "UPI"],
      },
    ],
  };
};

// Consolidated useHead with OG tags, meta data, canonical tag, and structured data for category pages
// Use computed properties for reactive updates when filters change
// Only applies when isCategoryPage is true (computed properties handle the conditional logic)
useHead({
  title: computed(() => isCategoryPage.value ? metaTitle.value : undefined),
  meta: computed(() => {
    if (!isCategoryPage.value) return [];
    const flatType = dynamicCategoryName.value || categoryValue.value || slugToTitle(propertySlug);
    const location = dynamicAreaName.value || slugToTitle(area) || 'Bangalore';
    
    return [
      ...ogTags.value.meta,
      // Additional category-specific meta tags
      {
        name: "keywords",
        content: `${flatType} flats ${location}, apartments ${location}, rental homes ${location}, ${flatType} properties ${location}, premium flats bangalore`
      }
    ];
  }),
  link: computed(() => {
    if (!isCategoryPage.value) return [];
    // Filter out canonical from ogTags since we're adding our own
    const ogLinksFiltered = ogTags.value.link.filter(link => link.rel !== 'canonical');
    
    return [
      ...ogLinksFiltered,
      // Self-referring canonical tag for category pages
      { rel: 'canonical', href: currentUrl.value },
      // Add preconnect for CDN performance
      { rel: 'preconnect', href: 'https://kots-world.b-cdn.net' },
      { rel: 'dns-prefetch', href: 'https://kots-world.b-cdn.net' }
    ];
  }),
  script: computed(() => {
    if (!isCategoryPage.value) return [];
    return [
      {
        type: "application/ld+json",
        children: () => JSON.stringify(generateCategoryStructuredData()),
        key: 'category-structured-data'
      }
    ];
  })
});

// Structured Data Implementation - Watch for property changes
// Note: Structured data is now consolidated in the main useHead above
// This watch is kept for any future dynamic updates if needed
watch([property, availableFlats, nearbyPlaces], () => {
  // Schema data is now consolidated in the main useHead call above
  // This watch ensures schema updates when nearby places are loaded
}, { immediate: true });

const activeTab = ref("about");

const tabs = [
  { id: "about", label: "About" },
  { id: "property-features", label: "Property Features" },
  { id: "virtual-tour", label: "Virtual Tour" },
  { id: "location", label: "Location" },
];

const activeSection = ref("about");

const scrollToSection = (id) => {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  }
};

const handleScroll = () => {
  const offsets = tabs.map((tab) => {
    const el = document.getElementById(tab.id);
    return el ? el.getBoundingClientRect().top : Infinity;
  });
  const index = offsets.findIndex((offset) => offset > 80); // 80px for header offset
  activeSection.value = tabs[Math.max(0, index - 1)].id;
};

onMounted(() => {
  window.addEventListener("scroll", handleScroll);
});
onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});

// / Reactive data
const show360View = ref(false);
const selectedThumbnail = ref(0);

// Thumbnail data for 360° tour
const thumbnails = ref([
  {
    src: "https://files.kuula.io/6568-32b9-1aed-6735/01-cover.jpg?ck=774667+",
    alt: "Entrance",
  },
  {
    src: "https://files.kuula.io/6568-32b9-1aed-c368/01-cover.jpg?ck=912569",
    alt: "Room",
  },
  {
    src: "https://files.kuula.io/6568-32b9-1aed-0439/01-cover.jpg?ck=989725",
    alt: "Garden",
  },
  {
    src: "https://files.kuula.io/6568-32b9-1aed-d211/01-cover.jpg?ck=6849",
    alt: "Balcony",
  },
  {
    src: "https://files.kuula.io/6568-32b9-1aed-8112/01-cover.jpg?ck=701283",
    alt: "Kitchen",
  },
  {
    src: "https://files.kuula.io/6568-32b9-1aed-9133/01-cover.jpg?ck=282144",
    alt: "Bathroom",
  },
  {
    src: 'https://files.kuula.io/6568-32b9-1aed-a158/01-cover.jpg?ck=736166"',
    alt: "Outside",
  },
]);

// Methods
const toggleVideoPlay = () => {
  show360View.value = true;
};

const zooming = ref(false);

const selectThumbnail = (index) => {
  selectedThumbnail.value = index;
  zooming.value = false;
  nextTick(() => {
    zooming.value = true;
  });
};

const showFullAbout = ref(false);

// Helper function to get about preview from API data or fallback
const getAboutPreview = () => {
  if (property.value?.locationDescription) {
    return property.value.locationDescription.length > 150
      ? property.value.locationDescription.substring(0, 150) + "..."
      : property.value.locationDescription;
  }
  return aboutPreview;
};

const aboutPreview = `Kots Abode is a premium living space offering studio flats and
1BHK for rent in Maithri layout locality that is ready to move in. These 1BHK homes are better-q`;

const aboutFull = `Kots Abode is a premium living space offering studio flats and
1BHK for rent in Maithri layout locality that is ready to move in. These 1BHK homes are better value for money than the other surrounding rental houses. The apartments are fully-furnished with top-quality furniture. The living room is provided with a sofa-cum-bed that can be used to accommodate a friend over or a family member for a night. These flats have well-designed infrastructure for the new-age tenants, having ample storage spaces in the bedroom and kitchen with cupboards and cabinets. The modular kitchens in all the studios and 1BHK for rent in Whitefield are fully equipped with appliances like induction stoves, refrigerators, microwaves, and chimneys. Amenities like high-speed internet and water and power backup are available. Housekeeping services can be availed at an additional service cost. Laundry area is also available for tenants with washers and dryers on the terrace. There is 24/7 security surveillance in the building, ensuring the safety of the residents. A stunning rooftop garden allows residents to unwind at any given hour. There is an enclosed 2-wheeler and 4-wheeler parking space for residents to avail of based on availability. Come live premium with Kots today!`;

// Props
const props = defineProps({
  projectCount: {
    type: Number,
    default: 19,
  },
  nearLocation: {
    type: String,
    default: "KOTS ABODE",
  },
  location: {
    type: String,
    default: "Whitefield",
  },
  //   properties: {
  //     type: Array,
  //     default: () => [
  //       {
  //         id: 1,
  //         name: "KOTS NEUF",
  //         location: "Whitefield",
  //         priceFrom: 20800,
  //         types: ["Studio", "1 BHK", "2 BHK"],
  //         availability: "27 flats available",
  //         status: null,
  //         image: "/api/placeholder/400/300",
  //       },
  //       {
  //         id: 2,
  //         name: "KOTS QUATRE",
  //         location: "Whitefield",
  //         priceFrom: 32800,
  //         types: ["1 BHK"],
  //         availability: "Only 2 flats available",
  //         status: "Filling fast",
  //         image: "/api/placeholder/400/300",
  //       },
  //       {
  //         id: 3,
  //         name: "KOTS RUE",
  //         location: "Marathahalli",
  //         priceFrom: 34800,
  //         types: ["1 BHK"],
  //         availability: "Only 2 flats available",
  //         status: "Filling fast",
  //         image: "/api/placeholder/400/300",
  //       },
  //     ],
  //   },
});

// Refs
const cardsContainer = ref(null);
const canScrollLeft = ref(false);
const canScrollRight = ref(true);

// Methods
const scrollLeft = () => {
  if (cardsContainer.value) {
    cardsContainer.value.scrollBy({ left: -400, behavior: "smooth" });
  }
};

const scrollRight = () => {
  if (cardsContainer.value) {
    cardsContainer.value.scrollBy({ left: 400, behavior: "smooth" });
  }
};

const updateScrollButtons = () => {
  if (cardsContainer.value) {
    const { scrollLeft, scrollWidth, clientWidth } = cardsContainer.value;
    canScrollLeft.value = scrollLeft > 0;
    canScrollRight.value = scrollLeft < scrollWidth - clientWidth - 1;
  }
};

const getBadgeClass = (availability) => {
  if (!availability) return "";
  if (availability.includes("Only")) return "bg-red-500 bg-opacity-90";
  return "bg-black/65 bg-opacity-90";
};

const formatPrice = (price) => {
  if (typeof price !== "number") return "";
  return price.toLocaleString("en-IN");
};

const navigateToProperty = (property) => {
  // Navigate to property details page
  //console.log("Navigate to property:", property.id);
  // You can use Nuxt router here: navigateTo(`/property/${property.id}`)
};

// Helper function to get carousel property image
const getCarouselPropertyImage = (carouselProperty) => {
  if (
    carouselProperty.featuredImage &&
    carouselProperty.featuredImage.savedName
  ) {
    return `https://kots-world.b-cdn.net/Final/categoryImages/thumb/${carouselProperty.featuredImage.savedName}`;
  }
  if (carouselProperty.image && carouselProperty.image.length > 0) {
    return `https://kots-world.b-cdn.net/Final/categoryImages/thumb/${carouselProperty.image[0].savedName}`;
  }
  return "https://kots-world.b-cdn.net/Final/assets/images/f-logo.png";
};

// Navigate to carousel property
const navigateToCarouselProperty = (carouselProperty) => {
  if (carouselProperty.userFriendlyUrl) {
    navigateTo(carouselProperty.userFriendlyUrl);
  }
};

function scrollToFlats() {
  const el = document.getElementById("flats-available");
  if (el) {
    el.scrollIntoView({ behavior: "smooth" });
  }
}

function goToProperty(property) {
  // Use flat ID if available, otherwise fallback to property ID
  const userFriendlyUrl = property?.userFriendlyUrl || "/";
  router.push(userFriendlyUrl);
}
function goToPayment(flat) {
  // Use flat ID if available, otherwise fallback to property ID
  const id =
    flat?.flatId || property.value?.id || property.value?.property_id || "";
  // router.push(`/payment/${id}`);
  router.push(flat.userFriendlyUrl);
}

// Lifecycle
onMounted(() => {
  if (cardsContainer.value) {
    cardsContainer.value.addEventListener("scroll", updateScrollButtons);
    updateScrollButtons();
  }
});

onUnmounted(() => {
  if (cardsContainer.value) {
    cardsContainer.value.removeEventListener("scroll", updateScrollButtons);
  }
});

// Structured Data Implementation - Added after all computed properties are defined
const seoReady = ref(false);

onMounted(() => {
  // Ensure all computed properties are ready before generating schema
  nextTick(() => {
    seoReady.value = true;
  });
});

// Note: Structured data is now consolidated in the main useHead call above
// This additional watch is kept for future dynamic updates if needed
</script>

<style scoped>
.mt-10 {
  margin-top: 7em;
}

/* Hide scrollbar for thumbnail navigation */
.overflow-x-auto::-webkit-scrollbar {
  display: none;
}

.overflow-x-auto {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scale-110 {
  transform: scale(1.1);
  transition: transform 0.3s;
}

/* Image styles - replacing Tailwind classes with plain CSS */
.img-property-main {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease;
}

.img-property-main:hover {
  opacity: 0.9;
}

.img-property-thumbnail {
  width: 4rem;
  height: 4rem;
  object-fit: cover;
  border-radius: 0.25rem;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.img-property-thumbnail-active {
  border-color: #afa11e;
}

.img-property-thumbnail-inactive {
  border-color: transparent;
  opacity: 0.7;
}

.img-property-thumbnail-inactive:hover {
  opacity: 1;
}

@media (min-width: 768px) {
  .img-property-thumbnail {
    width: 230px;
  }
}

.img-property-modal {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 0.5rem;
}

.img-property-full {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.img-flat-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 0.5rem;
}

.img-carousel-property {
  width: auto;
  max-width: 85%;
  height: auto;
  object-fit: cover;
  display: block;
  border-radius: 25px;
}

html {
  scroll-behavior: smooth;
}

.scrollbar-hide {
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* Responsive banner images */
.banner-responsive {
  background-image: url('https://kots-world.b-cdn.net/Final/bannerImages/full/gradient_one-min.png');
}

@media (max-width: 768px) {
  .banner-responsive {
    background-image: url('https://kots-world.b-cdn.net/Final/bannerImages/full/landing_page_gradient_image_two_1.png');
  }
}

/* Responsive mobile adjustments */
@media (max-width: 768px) {
  .min-w-80 {
    min-width: 280px;
  }
}
</style>