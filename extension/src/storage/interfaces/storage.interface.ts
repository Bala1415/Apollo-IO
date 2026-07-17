export interface IStorageService {
  get<T>(key: string): Promise<T | null>
  set<T>(key: string, value: T): Promise<void>
  remove(key: string): Promise<void>
  clear(): Promise<void>
  keys(): Promise<string[]>
}

export interface IIndexedDBService {
  open(storeName: string): Promise<void>
  getItem<T>(storeName: string, key: string): Promise<T | null>
  setItem<T>(storeName: string, key: string, value: T): Promise<void>
  deleteItem(storeName: string, key: string): Promise<void>
  getAllItems<T>(storeName: string): Promise<T[]>
  clear(storeName: string): Promise<void>
}
