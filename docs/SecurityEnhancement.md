# 보안 강화 방안

## 데이터베이스 격리

- API Gateway 외 모든 인스턴스는 `private subnet` 으로 격리
- 데이터베이스 접근은 반드시 DB 접근용 서버(리버스 프록시)를 거쳐야 함
- 데이터베이스는 DB 프록시 서버에 대한 접근만 허용(IP binding)

```
Internet

    ↓
    
API Gateway (Public Subnet)

    ↓ (NAT Gateway/Private Link)
    
API 서버 (Private Subnet)

    ↓ (Internal Network Only)
    
DB 접근용 서버 (Private Subnet)

    ↓ (IP Whitelist + Port Restriction)
    
Database (Isolated Subnet)

    ↑
    
암호화 키 저장소 (HSM/KMS)
```

## 신뢰도 높은 Secret Key 관리 서비스

AWS KMS, AWS CloudHSM 등 신뢰도 높은 비밀 키 관리 서비스를 이용해 안전하게 저장

- 최근 SKT 데이터베이스가 털린 이유가 secret key를 public 서버에 저장했기 때문이라고 함
- public 서버에 침투해 sercret key를 획득하고 이를 통해 private 서버에 침투할 수 있었음
- 심지어 private 서버에 DB 서버에 접속하기 위한 secret key가 있었다고 함

## 데이터베이스 내 민감 정보 암호화

### 필드 레벨 암호화

- 특정 컬럼에 대한 데이터 암호화
- 데이터베이스 엔진 내 암호화 함수를 사용한 데이터 암호화

### TDE (투명한 데이터 암호화)

- 데이터베이스 파일 전체 암호화

### RLS (행 레벨 보안)

- 행 단위 접근 권한 설정 가능
- 사용자별 데이터 격리 가능

