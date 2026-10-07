export interface Service {
  name: string;
  port: number;
}

// 展示名（中文/英文）在 i18n 资源 `services.<name>` 键下，不在此处冗余。
export const services: Service[] = [
  { name: 'identity-service', port: 11001 },
  { name: 'profile-service', port: 11002 },
  { name: 'tenant-service', port: 11003 },
  { name: 'session-service', port: 11004 },
  { name: 'mfa-service', port: 11005 },
  { name: 'oauth-service', port: 11006 },
  { name: 'wallet-service', port: 11011 },
  { name: 'point-service', port: 11012 },
  { name: 'audit-service', port: 11013 },
  { name: 'notification-service', port: 11014 },
  { name: 'communication-service', port: 11015 },
  { name: 'storage-service', port: 11016 },
  { name: 'billing-service', port: 11017 },
  { name: 'compliance-service', port: 11018 },
  { name: 'status-service', port: 11019 },
  { name: 'secret-service', port: 11020 },
  { name: 'saml-service', port: 11021 },
  { name: 'pay-service', port: 11022 },
  { name: 'thirdparty-service', port: 11023 },
  { name: 'verification-service', port: 11024 },
  { name: 'rbac-service', port: 11025 },
  { name: 'gateway-service', port: 11080 },
  { name: 'hash-service-standard', port: 11026 },
  { name: 'hash-service-sm', port: 11027 },
  { name: 'captcha3d-service', port: 11028 },
  { name: 'config-service', port: 11007 },
  { name: 'stream-service', port: 11029 },
];

export const serviceByName = new Map(services.map(s => [s.name, s]));
