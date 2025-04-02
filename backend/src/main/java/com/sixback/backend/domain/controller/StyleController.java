package com.sixback.backend.domain.controller;

import com.sixback.backend.common.service.RedisService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.sixback.backend.common.dto.ResponseDto;
import com.sixback.backend.domain.dto.StyleInfoListDto;
import com.sixback.backend.domain.dto.StyleMakeupReqDto;
import com.sixback.backend.domain.dto.StyleResultDto;
import com.sixback.backend.domain.service.StyleService;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.util.concurrent.CompletableFuture;

/**
 * 스타일 화장 관련 요청을 처리하는 컨트롤러.
 */
@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/market/{marketId}/styles")
public class StyleController {
	private final StyleService styleService;

	/**
	 * 화장 스타일 목록을 조회하는 메서드.
	 *
	 * @param marketId 요청한 마켓의 ID.
	 * @param page 페이지 번호 (기본값: 0).
	 * @param size 페이지 당 항목 수 (기본값: 10).
	 * @return 스타일 목록(StyleInfoListDto)과 상태 코드.
	 */
	@GetMapping
	public ResponseEntity<?> findAllStyle(@PathVariable("marketId") Long marketId,
		@Min(0) @RequestParam(defaultValue = "0", value = "page") int page,
		@Min(1) @RequestParam(defaultValue = "10", value = "size") int size) {
		// 스타일 목록 조회
		StyleInfoListDto styleInfoListDto = styleService.findAllStyle(marketId, page, size);
		return new ResponseEntity<>(new ResponseDto<>("A00", styleInfoListDto), HttpStatus.OK);
	}

	/**
	 * 가상 화장을 생성하는 메서드.
	 *
	 * @param marketId 요청한 마켓의 ID.
	 * @param styleMakeupReqDto 가상 화장(적용 스타일 번호, 사용자 이미지) 요청 DTO.
	 * @return 생성된 가상 화장 결과(StyleResultDto)와 상태 코드.
	 */
	@PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
	public Mono<ResponseEntity<ResponseDto<StyleResultDto>>> createStyleMakeup(
		@PathVariable("marketId") Long marketId,
		@Valid @ModelAttribute StyleMakeupReqDto styleMakeupReqDto) {
		// 스타일 가상 화장 요청 처리
		return styleService.createStyleMakeup(marketId, styleMakeupReqDto)
			.map(styleResultDto -> new ResponseEntity<>(new ResponseDto<>("A00", styleResultDto), HttpStatus.OK))
			// 가상 화장이 생성된 후 다른 스타일을 미리 가져옴 (pre-fetching)
			.doOnSuccess(response -> styleService.prefetchOtherStyles(marketId, styleMakeupReqDto));
	}

/*
	// 방식2: Redis에 해당 합성이미지가 없었을 때만 prefetch 수행
	@PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
	public Mono<ResponseEntity<ResponseDto<StyleResultDto>>> createStyleMakeup3(
			@PathVariable("marketId") Long marketId,
			@Valid @ModelAttribute StyleMakeupReqDto styleMakeupReqDto) {

		// 캐시 키 미리 생성
		String currentStyleCacheKey = styleService.generateCacheKey(marketId, styleMakeupReqDto.getStyleId(), styleMakeupReqDto);

		// 먼저 캐시 확인
		return Mono.fromCallable(() -> redisService.getData(currentStyleCacheKey, String.class))
				.flatMap(cachedImage -> {
					log.info("HoHoHoHo");
					// 캐시 히트: 캐시된 결과를 사용하고 prefetch 없이 즉시 반환
					StyleResultDto result = styleService.buildStyleResultDto(cachedImage, styleMakeupReqDto.getStyleId(), marketId);
					return Mono.just(new ResponseEntity<>(new ResponseDto<>("A00", result), HttpStatus.OK));
				})
				.switchIfEmpty(
						// 캐시 미스: 요청된 스타일 처리 후 prefetch 실행
						styleService.createStyleMakeup(marketId, styleMakeupReqDto)
								.map(styleResultDto -> new ResponseEntity<>(new ResponseDto<>("A00", styleResultDto), HttpStatus.OK))
								.doOnSuccess(response -> {
									// 캐시 미스인 경우에만 prefetch 실행
									styleService.prefetchOtherStyles(marketId, styleMakeupReqDto);
									log.info("Hello");
								})
				);
		}
	*/

	/**
	 * 현재 스타일에 사용된 모든 상품 위치 또는 특정 상품의 상세 정보를 조회하는 메서드.
	 *
	 * @param marketId 요청한 마켓의 ID.
	 * @param styleId 조회할 스타일의 ID.
	 * @param optionId 특정 상품의 ID (선택 사항).
	 * @return 사용된 상품 위치 또는 상세 정보를 담은 ResponseDto와 상태 코드.
	 */
	@GetMapping("/{styleId}")
	public ResponseEntity<?> findUseOptionInfo(@PathVariable("marketId") Long marketId,
		@PathVariable("styleId") Long styleId, @RequestParam(value = "optionId", required = false) Long optionId) {
		// 사용된 상품 위치 또는 상세 정보 조회
		Object useOptionInfo = styleService.findUseGoodsOptionInfo(marketId, styleId, optionId);
		return new ResponseEntity<>(new ResponseDto<>("A00", useOptionInfo), HttpStatus.OK);
	}
}
